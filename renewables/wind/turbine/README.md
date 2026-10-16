# Wind turbine with Scale

Replaces the deprecated `wind-turbine` app example for
[sandialabs/sceptre-phenix-apps#95](https://github.com/sandialabs/sceptre-phenix-apps/issues/95)
and [sandialabs/sceptre-phenix-topologies#21](https://github.com/sandialabs/sceptre-phenix-topologies/issues/21).
One nested-minimega VM hosts six OT-sim containers; a second VM runs
Elasticsearch 8 and Grafana. No HELICS broker, OpenDSS, or SCADA client is
required for this standalone demonstration.

The original turbine model was developed for the DOE Wind Energy Technology
Office-funded Wind Reference Architecture project at NREL, using OT-sim's
anemometer and power-output modules. This example migrates that model from
the standalone app to the Scale plugin.

Included files:

- `phenix-configs/`: Scenario v2 using `scale`/`wind_turbine` and Topology v1.
- `phenix-injects/grafana/`: Elasticsearch configuration, Grafana datasource,
  dashboard provisioning, and a two-panel dashboard with a stable datasource UID.
- `phenix-injects/flows.json`: a new, optional Node-RED `GET /health` flow using
  built-in nodes only; **not** the original project's unpublished control flow.
  OT-sim modules implement turbine control and physics without Node-RED.
- `phenix-images/`: nested-minimega VM setup, Grafana VM setup, and OT-sim rootfs
  recipe. The older `ot-sim.yml` and `grafana.yml` image configs are retained for
  historical reference; this Scale example uses the build commands below.
- `fetch_weather.py`: checksum-verified public replay-data download.

App implementation, rootfs staging, and Node-RED mount fixes live in the
companion [sceptre-phenix-apps repository](https://github.com/sandialabs/sceptre-phenix-apps).
Install that companion change before deploying this migrated example; the
deprecated standalone `wind-turbine` executable is not used.

## Weather data and provenance

The original example's dataset is publicly available in both
[sceptre-phenix-topologies](https://github.com/sandialabs/sceptre-phenix-topologies/blob/ad94013d68f65794e597980e4c0e9e4230ca57a5/renewables/wind/turbine/phenix-injects/weather.csv)
and [patsec/ot-sim](https://github.com/patsec/ot-sim/blob/9dc33047ff9fb474e61c8931c7dac7bf98df38ef/data/weather.csv).
Both Git LFS pointers identify the **same** 6,384,023-byte file:

```text
SHA-256 35d0c31dfca5135eb2b30781006b218862768a5c4c5bddb444f84663b56207f7
```

Download actual LFS contents, not the small pointer returned by a raw Git URL:

```bash
python3 renewables/wind/turbine/fetch_weather.py
```

The downloader pins the topology repository revision, verifies SHA-256 and all
nine configured numeric columns, and reports 42,000 samples. OT-sim replays one
row per second, independently of the CSV timestamps: **11 hours 40 minutes**.
The current upstream anemometer does not wrap at EOF; restart the experiment
before replay ends. The file is already tracked here through Git LFS; use
`git lfs pull` or the downloader if the checkout contains only a pointer.
Consult the upstream repository
license and any applicable dataset terms before redistributing it. The upstream
example describes the NREL/WETO project, but does not document this dataset's
measurement site or original collection license; do not infer those details.
No private dataset is needed.

The new flow and Grafana files in this directory are authored for this example;
the historical Grafana files are also public in the topology repository above.

## Prerequisites

- An isolated **Linux x86-64** phēnix/minimega deployment with KVM, Open vSwitch,
  miniccc, Docker, and image-building support (vmdb2).
- The companion `phenix-apps` changes installed inside the phēnix runtime:
  `container_template.rootfs_source` support and the Node-RED mounted-flow fix.
- At least 12 GiB available guest RAM plus host overhead, and sufficient disk
  space for two VM builds and the exported OT-sim rootfs.
- Internet access during setup only; runtime uses the isolated `ot` network.

The following commands assume a host checkout at
`/phenix/sceptre-phenix-topologies`, with `/phenix` shared at the same path by the
`phenix` and `minimega` containers. Adjust paths to your bind mounts.
Run Docker commands on the host, and `phenix` commands inside its container.
Do not attach this deliberately unauthenticated lab to production networks:
Elasticsearch is unauthenticated, Grafana permits anonymous **Viewer** access,
and the optional Node-RED editor has no authentication.

## Build the three image artifacts

From the host checkout:

```bash
cd /phenix/sceptre-phenix-topologies
mkdir -p renewables/wind/turbine/build/minimeta-overlay/usr/local/bin
mkdir -p /phenix/images /phenix/vmdb
docker cp minimega:/opt/minimega/bin/minimega \
  renewables/wind/turbine/build/minimeta-overlay/usr/local/bin/minimega
docker cp minimega:/opt/minimega/bin/miniccc /phenix/miniccc

docker build --platform linux/amd64 -t wind-turbine-rootfs \
  -f renewables/wind/turbine/phenix-images/Dockerfile \
  renewables/wind/turbine/phenix-images
docker create --name wind-turbine-rootfs-export wind-turbine-rootfs
docker export wind-turbine-rootfs-export | gzip > /phenix/images/otsimfs.tgz
docker rm wind-turbine-rootfs-export
```

The Dockerfile pins the OT-sim source-revision tag `9dc3304`. Use
`--build-arg OTSIM_IMAGE=ghcr.io/patsec/ot-sim@sha256:...` to pin an immutable
registry digest. Set `--build-arg MINIMEGA_IMAGE=...` to the **same release**
as your running minimega container; its default is `master`.
The init program enables veth interfaces, starts miniccc on `/cc`, and starts
OT-sim. Main controllers also forward/NAT private-controller telemetry.
Docker export is a root filesystem tar archive, **not** `docker save`.

Create the VM image configs using the core's default phēnix startup scripts:

```bash
docker exec phenix phenix image create -r jammy -s 20G \
  -P openvswitch-switch,iproute2,iptables,libpcap0.8 \
  -O /phenix/sceptre-phenix-topologies/renewables/wind/turbine/build/minimeta-overlay \
  -T /phenix/sceptre-phenix-topologies/renewables/wind/turbine/phenix-images/minimeta.sh minimeta
docker exec phenix phenix image create -r jammy -s 30G \
  -T /phenix/sceptre-phenix-topologies/renewables/wind/turbine/phenix-images/grafana.sh grafana
docker exec phenix phenix image build -x -o /phenix/vmdb minimeta
docker exec phenix phenix image build -x -o /phenix/vmdb grafana
docker exec phenix phenix image inject-miniexe /phenix/miniccc /phenix/vmdb/minimeta.qc2
docker exec phenix phenix image inject-miniexe /phenix/miniccc /phenix/vmdb/grafana.qc2
cp /phenix/vmdb/minimeta.qc2 /phenix/vmdb/grafana.qc2 /phenix/images/
```

Existing configs with these names must be reused or deliberately replaced.
Image scripts are snapshotted at `image create`; recreate/update the config
after editing scripts. An existing image-build `.tar` cache can mask package
changes. The minimeta recipe names its single virtio NIC `ens1`, matching Scale's
trunk-bridge setup, and starts nested minimega before the phēnix startup service.
No inner KVM support is required: inner guests are containers.

## Stage assets and deploy

```bash
python3 renewables/wind/turbine/fetch_weather.py
mkdir -p /phenix/injects/wind-turbine
cp -R renewables/wind/turbine/phenix-injects/. /phenix/injects/wind-turbine/
docker exec phenix phenix config create \
  /phenix/sceptre-phenix-topologies/renewables/wind/turbine/phenix-configs/topology.yml \
  /phenix/sceptre-phenix-topologies/renewables/wind/turbine/phenix-configs/scenario.yml
docker exec phenix phenix experiment create wind-turbine-scale \
  -t wind-turbine-scale -s wind-turbine-scale
docker exec phenix phenix experiment schedule wind-turbine-scale single-node
docker exec phenix phenix experiment start wind-turbine-scale
```

Scale generates `wtg-1`; do **not** retain the six hand-written turbine VMs
from the deprecated topology. `rootfs_source` and `replayData` are head-node
paths: Scale injects them into each generated VM. Containers mount their
generated XML/flow directory at `/etc/ot-sim` and replay data at `/shared`.
The `ot` VLAN is allocated by phēnix; nested minimega receives its numeric ID.

Increase `count` for more turbines. `containers_per_node` must be a positive
multiple of six so a turbine's private network never spans host VMs.
Addresses start at `192.168.100.10`; keep allocations below the Grafana address
`.250` (at most 240 turbines with this subnet/address plan).
Tune VM and container memory before scaling.

## Verify a live experiment

```bash
docker exec phenix phenix vm info wind-turbine-scale
docker exec minimega mm namespace wind-turbine-scale cc clients
docker exec minimega mm namespace wind-turbine-scale \
  cc tunnel grafana 30000 localhost 3000
docker exec minimega mm namespace wind-turbine-scale \
  cc tunnel grafana 39200 localhost 9200
curl --fail 'http://localhost:39200/_cluster/health'
curl --fail 'http://localhost:39200/wind-turbine-*/_count'
```

Open <http://localhost:30000/d/wind-turbine> after Elasticsearch starts and
telemetry arrives. Expect nonzero document counts, changing wind speed, and
power output in MW. The bundled dashboard uses `@timestamp`, `field`, `value`,
`source`, and `labels.turbine` emitted by OT-sim's ground-truth module.
Access forwarded ports through an SSH tunnel if minimega is on a remote host.

For inner diagnostics, run `mm namespace wind cc clients` inside `wtg-1`.
Expect six clients named `wtg-1-{main-controller,signal-converter,yaw-controller,blade-1,blade-2,blade-3}`.
From that VM, `curl --fail http://192.168.100.10:1880/health` checks the
optional flow only, not the physics pipeline. Inspect each container's
`/etc/ot-sim/log.txt` and the VM's `/scale/wtg-1/<1..6>/` files for module errors.

If no data arrives, check Elasticsearch readiness first, then inner miniccc
connections, Modbus reachability, and weather column mappings. A missing flow
must use singular `node-red.flow`, not `flows`; it is copied into the container's
mounted configuration directory. Remove the `node-red` section to disable it.

Stop the lab when finished:

```bash
docker exec phenix phenix experiment stop wind-turbine-scale
```

## Local validation without VMs

The regression test assembles these exact resources, substitutes temporary
asset paths, and exercises real configure/post-start generation. It checks all
six XML files, the config tarball, rootfs/weather injections, flow mounting,
network addresses, datasource UID, and dashboard queries:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '../sceptre-phenix-apps/src/python[dev]'
PHENIX_LOG_FILE="" python -m pytest renewables/wind/turbine/tests
```

Use Python 3.12+ and adjust the companion checkout path if needed. The apps
repository keeps independent plugin regression tests and does not require this
topology checkout. These tests use the installed companion package.

This is not a live KVM/Elasticsearch/Grafana integration test. Image builds and
the live checks above must run on the target Linux deployment.
