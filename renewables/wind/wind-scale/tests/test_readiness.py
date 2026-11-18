import importlib.util
import io
import json
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest.mock import MagicMock
from urllib.error import HTTPError, URLError

import pytest

EXAMPLE = Path(__file__).resolve().parents[1]


@pytest.fixture
def readiness():
    spec = importlib.util.spec_from_file_location(
        "wind_scale_readiness", EXAMPLE / "phenix-images/readiness.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def interface(name, addressed=True):
    return {
        "ifname": name,
        "addr_info": [{"family": "inet", "scope": "global"}] if addressed else [],
    }


@pytest.mark.parametrize(
    ("interfaces", "reason"),
    [
        ([], "no container veth interfaces"),
        ([interface("lo")], "no container veth interfaces"),
        ([interface("veth0", False)], "assignment on veth0"),
        ([interface("veth0"), interface("veth1", False)], "assignment on veth1"),
        ([interface("veth0")], None),
        ([interface("veth0"), interface("veth1")], None),
    ],
)
def test_all_interfaces_need_addresses(readiness, monkeypatch, interfaces, reason):
    run = MagicMock(
        return_value=subprocess.CompletedProcess([], 0, json.dumps(interfaces))
    )
    monkeypatch.setattr(readiness.subprocess, "run", run)
    result = readiness.check_network()
    if reason is None:
        assert result is None
    else:
        assert reason in result
    run.assert_called_once_with(
        ["ip", "-j", "-4", "address", "show"],
        check=True,
        capture_output=True,
        text=True,
    )


def test_network_command_failure_is_not_hidden(readiness, monkeypatch):
    error = subprocess.CalledProcessError(1, "ip")
    monkeypatch.setattr(readiness.subprocess, "run", MagicMock(side_effect=error))
    with pytest.raises(subprocess.CalledProcessError):
        readiness.check_network()


@pytest.mark.parametrize(
    ("health", "ready"),
    [
        ({"status": "yellow", "timed_out": False}, True),
        ({"status": "green", "timed_out": False}, True),
        ({"status": "red", "timed_out": False}, False),
        ({"status": "yellow", "timed_out": True}, False),
        ({}, False),
    ],
)
def test_elastic_requires_ready_cluster(readiness, monkeypatch, health, ready):
    request = MagicMock(return_value=io.BytesIO(json.dumps(health).encode()))
    monkeypatch.setattr(readiness, "urlopen", request)
    assert (readiness.check_elastic("http://elastic:9200/", 2) is None) == ready
    request.assert_called_once_with(
        "http://elastic:9200/_cluster/health?wait_for_status=yellow&timeout=1s",
        timeout=2,
    )


@pytest.mark.parametrize(
    "error",
    [
        URLError("connection refused"),
        TimeoutError("timed out"),
        HTTPError("http://elastic:9200", 503, "unavailable", None, None),
    ],
)
def test_elastic_temporary_errors_are_reported(readiness, monkeypatch, error):
    monkeypatch.setattr(readiness, "urlopen", MagicMock(side_effect=error))
    assert "not reachable" in readiness.check_elastic("http://elastic:9200", 2)


@pytest.fixture
def config(tmp_path):
    path = tmp_path / "config.xml"
    path.write_text(
        "<ot-sim><ground-truth><elastic>"
        "<endpoint>http://elastic:9200</endpoint>"
        "</elastic></ground-truth></ot-sim>"
    )
    return str(path)


@pytest.fixture
def clock(readiness, monkeypatch):
    now = [0.0]
    monkeypatch.setattr(readiness.time, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        readiness.time, "sleep", lambda duration: now.__setitem__(0, now[0] + duration)
    )
    return now


def test_address_then_elastic_gate(readiness, config, clock, monkeypatch, capsys):
    network = MagicMock(side_effect=["waiting for IPv4", None, None])
    elastic = MagicMock(side_effect=["waiting for Elasticsearch", None])
    monkeypatch.setattr(readiness, "check_network", network)
    monkeypatch.setattr(readiness, "check_elastic", elastic)
    readiness.wait_ready(config, 10)
    assert network.call_count == 3
    assert elastic.call_count == 2
    assert clock[0] == 2
    stderr = capsys.readouterr().err
    assert "waiting for IPv4" in stderr
    assert "waiting for Elasticsearch" in stderr
    assert "dependencies ready" in stderr


@pytest.mark.parametrize("blocked", ["network", "elastic"])
def test_timeout_does_not_start_simulation(
    readiness, config, clock, monkeypatch, capsys, blocked
):
    monkeypatch.setattr(
        readiness,
        "check_network",
        lambda: "waiting for IPv4" if blocked == "network" else None,
    )
    monkeypatch.setattr(
        readiness, "check_elastic", lambda *args: "waiting for Elasticsearch"
    )
    with pytest.raises(TimeoutError, match="startup timed out: waiting for"):
        readiness.wait_ready(config, 3)
    assert clock[0] == 3
    assert "dependencies ready" not in capsys.readouterr().err


def test_missing_ground_truth_only_waits_for_network(
    readiness, config, clock, monkeypatch
):
    Path(config).write_text("<ot-sim/>")
    monkeypatch.setattr(readiness, "check_network", lambda: None)
    request = MagicMock()
    monkeypatch.setattr(readiness, "check_elastic", request)
    readiness.wait_ready(config, 1)
    request.assert_not_called()


def test_invalid_timeout_is_explicit(readiness, config):
    with pytest.raises(ValueError, match="timeout must be positive"):
        readiness.wait_ready(config, 0)


def test_init_orders_dependencies_before_cpu():
    init = (EXAMPLE / "phenix-images/init").read_text()
    assert init.index("/miniccc -family unix") < init.index("python3 ")
    assert init.index("python3 ") < init.index("exec ot-sim-cpu-module")
    dockerfile = (EXAMPLE / "phenix-images/Dockerfile").read_text()
    assert "COPY readiness.py /usr/local/lib/wind-scale/readiness.py" in dockerfile


def test_real_http_dependency_becomes_ready(readiness, tmp_path, monkeypatch):
    requests = []

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            if len(requests) == 1:
                self.send_response(503)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"yellow","timed_out":false}')

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), HealthHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        config = tmp_path / "config.xml"
        config.write_text(
            "<ot-sim><ground-truth><elastic>"
            f"<endpoint>http://127.0.0.1:{server.server_port}</endpoint>"
            "</elastic></ground-truth></ot-sim>"
        )
        monkeypatch.setattr(readiness, "check_network", lambda: None)
        readiness.wait_ready(str(config), 5)
        assert requests == [
            "/_cluster/health?wait_for_status=yellow&timeout=1s",
            "/_cluster/health?wait_for_status=yellow&timeout=1s",
        ]
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
