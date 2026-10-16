"""Download the public OT-sim replay dataset, verifying its Git LFS digest."""

import argparse
import csv
import hashlib
import io
from pathlib import Path
from urllib.request import urlopen

REVISION = "ad94013d68f65794e597980e4c0e9e4230ca57a5"
URL = (
    "https://media.githubusercontent.com/media/"
    f"sandialabs/sceptre-phenix-topologies/{REVISION}/"
    "renewables/wind/turbine/phenix-injects/weather.csv"
)
SHA256 = "35d0c31dfca5135eb2b30781006b218862768a5c4c5bddb444f84663b56207f7"
COLUMNS = (
    "Windspeed 58.2m",
    "Windspeed 36.6m",
    "Windspeed 15.0m",
    "Wind Direction 58.2m",
    "Wind Direction 36.6m",
    "Wind Direction 15.0m",
    "Temperature 58.2m",
    "Temperature 3.0m",
    "Barometric Pressure",
)


def fetch(destination: Path) -> int:
    with urlopen(URL, timeout=60) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError("weather.csv SHA-256 mismatch; refusing to write dataset")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8")))
    if not set(COLUMNS).issubset(reader.fieldnames or []):
        raise ValueError("weather.csv is missing required OT-sim weather columns")
    rows = 0
    for row in reader:
        for column in COLUMNS:
            float(row[column])
        rows += 1
    if not rows:
        raise ValueError("weather.csv has no replay samples")
    destination.write_bytes(data)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=Path(__file__).parent / "phenix-injects" / "weather.csv",
    )
    args = parser.parse_args()
    samples = fetch(args.destination)
    print(f"Verified {samples} samples ({samples} seconds of OT-sim replay)")
