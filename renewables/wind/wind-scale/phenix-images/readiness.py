"""Wait for miniccc addressing and Elasticsearch before starting OT-sim."""

import argparse
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from urllib.error import URLError
from urllib.request import urlopen


def check_network() -> str | None:
    result = subprocess.run(
        ["ip", "-j", "-4", "address", "show"],
        check=True,
        capture_output=True,
        text=True,
    )
    interfaces = [
        item for item in json.loads(result.stdout) if item["ifname"].startswith("veth")
    ]
    if not interfaces:
        return "no container veth interfaces"
    for interface in interfaces:
        if not any(
            address["family"] == "inet" and address["scope"] == "global"
            for address in interface["addr_info"]
        ):
            return f"waiting for miniccc IPv4 assignment on {interface['ifname']}"
    return None


def check_elastic(endpoint: str, timeout: float) -> str | None:
    url = endpoint.rstrip("/") + "/_cluster/health?wait_for_status=yellow&timeout=1s"
    try:
        with urlopen(url, timeout=timeout) as response:
            health = json.load(response)
    except (URLError, TimeoutError) as exc:
        return f"Elasticsearch is not reachable: {exc}"
    if health.get("timed_out") or health.get("status") not in ("yellow", "green"):
        return "Elasticsearch cluster is not yellow or green"
    return None


def wait_ready(config: str, timeout: float) -> None:
    if timeout <= 0:
        raise ValueError("readiness timeout must be positive")
    root = ET.parse(config).getroot()
    endpoint = root.findtext("ground-truth/elastic/endpoint")
    deadline = time.monotonic() + timeout
    previous = None
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f"OT-sim startup timed out: {previous}")
        reason = check_network()
        if reason is None and endpoint:
            reason = check_elastic(endpoint, min(2, remaining))
        if reason is None:
            print("OT-sim network and telemetry dependencies ready", file=sys.stderr)
            return
        if reason != previous:
            print(reason, file=sys.stderr)
            previous = reason
        time.sleep(min(1, max(0, deadline - time.monotonic())))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config")
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    wait_ready(args.config, args.timeout)
