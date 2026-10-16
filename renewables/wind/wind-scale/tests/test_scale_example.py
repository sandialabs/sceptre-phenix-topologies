import csv
import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from unittest.mock import MagicMock

import lxml.etree as ET
import pytest
import yaml
from phenix_apps.apps.scale.app import Scale
from phenix_apps.common import settings

EXAMPLE = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(("turbines", "density"), [(1, 6), (3, 12)])
def test_example_generates_real_artifacts(tmp_path, monkeypatch, turbines, density):
    scenario = yaml.safe_load((EXAMPLE / "phenix-configs/scenario.yml").read_text())
    topology = yaml.safe_load((EXAMPLE / "phenix-configs/topology.yml").read_text())
    profile = scenario["spec"]["apps"][0]["metadata"]["profiles"][0]
    profile["count"] = turbines
    profile["containers_per_node"] = density
    templates = profile["templates"]["default"]
    flow = EXAMPLE / "phenix-injects/flows.json"
    templates["main-controller"]["node-red"]["flow"] = str(flow)
    weather = tmp_path / "weather.csv"
    columns = templates["anemometer"]["weather"]["columns"]
    with weather.open("w") as file:
        writer = csv.writer(file)
        writer.writerow([column["name"] for column in columns])
        writer.writerow([1] * len(columns))
    templates["anemometer"]["weather"]["replayData"] = str(weather)
    rootfs = tmp_path / "otsimfs.tgz"
    with tarfile.open(rootfs, "w:gz"):
        pass
    profile["container_template"]["rootfs_source"] = str(rootfs)
    experiment = {
        "metadata": {"annotations": {"retained": "yes"}},
        "spec": {
            "experimentName": "wind-scale",
            "baseDir": str(tmp_path / "experiment"),
            "scenario": scenario["spec"],
            "topology": topology["spec"],
        },
        "status": {"vlans": {"ot": 200}},
    }
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps(experiment)))
    monkeypatch.setattr(settings, "PHENIX_DIR", str(tmp_path))
    app = Scale("scale", "configure")
    app.configure()
    assert app.experiment.metadata.annotations.retained == "yes"
    assert app.experiment.spec.topology.nodes[0].general.hostname == "grafana"
    nodes = app.experiment.spec.topology.nodes[1:]
    assert len(nodes) == (turbines * 6 + density - 1) // density

    xml_files = sorted(app.app_dir.glob("wtg-*/*/config.xml"))
    assert len(xml_files) == turbines * 6
    for path in xml_files:
        xml = ET.parse(path)
        assert xml.getroot().tag == "ot-sim"
        assert xml.findtext("ground-truth/elastic/endpoint") == (
            "http://192.168.100.250:9200"
        )
        assert xml.findtext("ground-truth/elastic/label") in {
            f"wtg-{i}" for i in range(1, turbines + 1)
        }
        if xml.find("node-red") is not None:
            assert xml.findtext("node-red/flow-path") == "/etc/ot-sim/node-red.json"
            assert (path.parent / "node-red.json").read_bytes() == flow.read_bytes()
            assert len(xml.findall("modbus")) == 5
            assert xml.find("dnp3") is not None
            assert xml.find("wind-turbine/power-output") is not None
        if xml.find("wind-turbine/anemometer") is not None:
            assert xml.findtext("wind-turbine/anemometer/data-path") == (
                "/shared/weather.csv"
            )
            assert {
                column.get("name")
                for column in xml.findall("wind-turbine/anemometer/weather-data/column")
            } == {column["name"] for column in columns}

    with tarfile.open(Path(app.exp_dir) / "wind-configs.tgz") as archive:
        names = archive.getnames()
        assert sum(name.endswith("/config.xml") for name in names) == turbines * 6
        assert sum(name.endswith("/node-red.json") for name in names) == turbines
    for node in nodes:
        injections = {item.dst: item.src for item in node.injections}
        assert injections["/scale/rootfs/otsimfs.tgz"] == str(rootfs)
        assert injections["/scale/shared/weather.csv"] == str(weather)
        assert "/wind-configs.tgz" in injections

    # Re-initialize from serialized output, as core does for each lifecycle stage.
    monkeypatch.setattr("sys.stdin", io.StringIO(app.experiment.to_json()))
    post_start = Scale("scale", "post-start")
    mm = MagicMock()
    monkeypatch.setattr("minimega.connect", lambda **kwargs: mm)
    post_start.post_start()
    assert mm.cc_send.call_count == len(nodes)
    scripts = [path.read_text() for path in sorted(post_start.files_dir.glob("*.mm"))]
    assert (
        sum(script.count("vm launch container ") for script in scripts) == turbines * 6
    )
    for script in scripts:
        assert "namespace wind" in script
        assert "vm config filesystem tar:/scale/rootfs/otsimfs.tgz" in script
        assert "vm config volume /shared/ /scale/shared/" in script
        assert "/scale/shared/otsimfs.tgz" not in script
        assert "vm config net wind-scale,200 wtg-" in script
        assert "vm config volume /etc/ot-sim/ /scale/wtg-" in script
    joined = "\n".join(scripts)
    for i in range(1, turbines + 1):
        assert f"cc exec ip addr add 192.168.100.{9 + i}/24 dev veth0" in joined
        for component in (
            "main-controller",
            "signal-converter",
            "yaw-controller",
            "blade-1",
            "blade-2",
            "blade-3",
        ):
            assert joined.count(f"vm launch container wtg-{i}-{component}\n") == 1


def test_example_provisioning_and_paths():
    topology = yaml.safe_load((EXAMPLE / "phenix-configs/topology.yml").read_text())
    for inject in topology["spec"]["nodes"][0]["injections"]:
        source = inject["src"].removeprefix("/phenix/injects/wind-scale/")
        assert (EXAMPLE / "phenix-injects" / source).is_file()
    grafana = EXAMPLE / "phenix-injects/grafana"
    datasource = yaml.safe_load((grafana / "elastic-data-source.yml").read_text())
    uid = datasource["datasources"][0]["uid"]
    dashboard = json.loads((grafana / "turbine-dashboard.json").read_text())
    assert dashboard["uid"] == "wind-turbine"
    for panel in dashboard["panels"]:
        assert panel["datasource"]["uid"] == uid
        assert panel["targets"][0]["metrics"][0]["field"] == "value"
    flow = json.loads((EXAMPLE / "phenix-injects/flows.json").read_text())
    ids = {node["id"] for node in flow}
    assert any(node.get("url") == "/health" for node in flow)
    for node in flow:
        for targets in node.get("wires", []):
            assert set(targets) <= ids


def test_legacy_example_is_separate():
    legacy = EXAMPLE.parent / "turbine"
    legacy_scenario = yaml.safe_load(
        (legacy / "phenix-configs/scenario.yml").read_text()
    )
    scenario = yaml.safe_load((EXAMPLE / "phenix-configs/scenario.yml").read_text())
    topology = yaml.safe_load((EXAMPLE / "phenix-configs/topology.yml").read_text())
    assert legacy_scenario["spec"]["apps"][0]["name"] == "wind-turbine"
    assert scenario["metadata"]["name"] == "wind-scale"
    assert topology["metadata"]["name"] == "wind-scale"
    assert scenario["spec"]["apps"][0]["name"] == "scale"
    profile = scenario["spec"]["apps"][0]["metadata"]["profiles"][0]
    assert profile["node_template"]["image"] == "wind-scale-minimeta.qc2"
    assert profile["container_template"]["rootfs_source"] == (
        "/phenix/images/wind-scale-otsimfs.tgz"
    )
    assert topology["spec"]["nodes"][0]["hardware"]["drives"][0]["image"] == (
        "wind-scale-grafana.qc2"
    )
    assert all(
        inject["src"].startswith("/phenix/injects/wind-scale/")
        for inject in topology["spec"]["nodes"][0]["injections"]
    )


@pytest.fixture
def downloader():
    spec = importlib.util.spec_from_file_location(
        "wind_example_fetch_weather", EXAMPLE / "fetch_weather.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_weather_download_validates_before_writing(downloader, tmp_path, monkeypatch):
    data = (",".join(downloader.COLUMNS) + "\n" + ",".join(["1"] * 9) + "\n").encode()
    monkeypatch.setattr(downloader, "urlopen", lambda *args, **kwargs: io.BytesIO(data))
    destination = tmp_path / "weather.csv"
    destination.write_text("keep existing data")
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        downloader.fetch(destination)
    assert destination.read_text() == "keep existing data"
    monkeypatch.setattr(downloader, "SHA256", hashlib.sha256(data).hexdigest())
    assert downloader.fetch(destination) == 1
    assert destination.read_bytes() == data


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (b"wrong-column\n1\n", "missing required"),
        (b"", "missing required"),
    ],
)
def test_weather_download_rejects_wrong_format(
    downloader, tmp_path, monkeypatch, data, message
):
    monkeypatch.setattr(downloader, "SHA256", hashlib.sha256(data).hexdigest())
    monkeypatch.setattr(downloader, "urlopen", lambda *args, **kwargs: io.BytesIO(data))
    destination = tmp_path / "weather.csv"
    with pytest.raises(ValueError, match=message):
        downloader.fetch(destination)
    assert not destination.exists()


@pytest.mark.parametrize("sample", [None, "not-a-number"])
def test_weather_download_rejects_missing_or_invalid_samples(
    downloader, tmp_path, monkeypatch, sample
):
    text = ",".join(downloader.COLUMNS) + "\n"
    if sample is not None:
        text += ",".join([sample] * 9) + "\n"
    data = text.encode()
    monkeypatch.setattr(downloader, "SHA256", hashlib.sha256(data).hexdigest())
    monkeypatch.setattr(downloader, "urlopen", lambda *args, **kwargs: io.BytesIO(data))
    destination = tmp_path / "weather.csv"
    with pytest.raises(
        ValueError, match=r"no replay samples|could not convert string to float"
    ):
        downloader.fetch(destination)
    assert not destination.exists()
