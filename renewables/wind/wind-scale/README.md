# Wind turbine with Scale

A separate Scale-based example for
[sandialabs/sceptre-phenix-apps#95](https://github.com/sandialabs/sceptre-phenix-apps/issues/95)
and [sandialabs/sceptre-phenix-topologies#21](https://github.com/sandialabs/sceptre-phenix-topologies/issues/21).
One nested-minimega VM hosts six OT-sim containers; a second VM runs
Elasticsearch 8 and Grafana. No HELICS broker, OpenDSS, or SCADA client is
required for this standalone demonstration.

The [legacy turbine example](../turbine/README.md) retains its original
standalone-app topology and assets. This directory owns its own resource names,
VM images, injection paths, and generated weather file, so neither setup
overwrites the other's files.

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
  recipe, including a bounded network/Elasticsearch readiness gate.
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
python3 renewables/wind/wind-scale/fetch_weather.py
```

The downloader pins the topology repository revision, verifies SHA-256 and all
nine configured numeric columns, and reports 42,000 samples. OT-sim replays one
row per second, independently of the CSV timestamps: **11 hours 40 minutes**.
The current upstream anemometer does not wrap at EOF; restart the experiment
before replay ends. The legacy example tracks this dataset through Git LFS;
the downloader writes a verified copy into this example's ignored
`phenix-injects/weather.csv`, without changing the legacy file.
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
mkdir -p renewables/wind/wind-scale/build/minimeta-overlay/usr/local/bin
mkdir -p /phenix/images /phenix/vmdb
docker cp minimega:/opt/minimega/bin/minimega \
  renewables/wind/wind-scale/build/minimeta-overlay/usr/local/bin/minimega
docker cp minimega:/opt/minimega/bin/miniccc /phenix/miniccc

# Use the exact same immutable minimega image as the running deployment.
MINIMEGA_IMAGE=$(docker inspect minimega --format '{{.Config.Image}}')
case "$MINIMEGA_IMAGE" in
  *@sha256:*) ;;
  *) echo "Start minimega from an immutable image digest first" >&2; exit 1 ;;
esac
docker build --platform linux/amd64 -t wind-turbine-rootfs \
  --build-arg MINIMEGA_IMAGE="$MINIMEGA_IMAGE" \
  -f renewables/wind/wind-scale/phenix-images/Dockerfile \
  renewables/wind/wind-scale/phenix-images
docker create --name wind-turbine-rootfs-export wind-turbine-rootfs
docker export wind-turbine-rootfs-export | gzip > /phenix/images/wind-scale-otsimfs.tgz
docker rm wind-turbine-rootfs-export
docker image inspect wind-turbine-rootfs > renewables/wind/wind-scale/build/rootfs-image.json
sha256sum /phenix/images/wind-scale-otsimfs.tgz \
  > renewables/wind/wind-scale/build/rootfs.sha256
```

The Dockerfile pins the amd64 OT-sim `9dc3304` image and a minimega reference
image by immutable SHA-256 digest. The build command overrides minimega with
your running deployment's digest so the inner miniccc and copied VM minimega
match. Configure your minimega deployment with an immutable image reference;
do not rely on a mutable `master` tag. A digest identifies a build input, not
proof that the full VM experiment has been validated.

The init program enables veth interfaces, starts miniccc on `/cc`, then waits
for global IPv4 addresses on **every** veth interface and for the configured
Elasticsearch cluster to reach yellow or green before starting any OT-sim
module. This lets miniccc assign addresses without racing protocol listeners
or OT-sim's one-shot index-template creation. The wait defaults to 300 seconds;
failure prints a diagnostic and exits nonzero rather than starting a broken
simulation. Edit the `--timeout` argument in the init recipe to change the
deadline. Main controllers also forward/NAT private-controller telemetry.
Docker export is a root filesystem tar archive, **not** `docker save`.

Create the VM image configs using the core's default phēnix startup scripts:

```bash
docker exec phenix phenix image create -r jammy -s 20G \
  -P openvswitch-switch,iproute2,iptables,libpcap0.8 \
  -O /phenix/sceptre-phenix-topologies/renewables/wind/wind-scale/build/minimeta-overlay \
  -T /phenix/sceptre-phenix-topologies/renewables/wind/wind-scale/phenix-images/minimeta.sh wind-scale-minimeta
docker exec phenix phenix image create -r jammy -s 30G \
  -T /phenix/sceptre-phenix-topologies/renewables/wind/wind-scale/phenix-images/grafana.sh wind-scale-grafana
docker exec phenix phenix image build -x -o /phenix/vmdb wind-scale-minimeta
docker exec phenix phenix image build -x -o /phenix/vmdb wind-scale-grafana
docker exec phenix phenix image inject-miniexe /phenix/miniccc /phenix/vmdb/wind-scale-minimeta.qc2
docker exec phenix phenix image inject-miniexe /phenix/miniccc /phenix/vmdb/wind-scale-grafana.qc2
cp /phenix/vmdb/wind-scale-minimeta.qc2 /phenix/vmdb/wind-scale-grafana.qc2 /phenix/images/
```

Existing configs with these names must be reused or deliberately replaced.
Image scripts are snapshotted at `image create`; recreate/update the config
after editing scripts. An existing image-build `.tar` cache can mask package
changes. The minimeta recipe names its single virtio NIC `ens1`, matching Scale's
trunk-bridge setup, and starts nested minimega before the phēnix startup service.
No inner KVM support is required: inner guests are containers.

The Grafana VM recipe pins Grafana **12.3.0** and Elasticsearch **8.19.5**,
and holds those packages. If a version is unavailable, the build fails; update
the pins deliberately and revalidate the dashboard rather than silently
installing another version. OS dependencies still use distribution mirrors,
so these recipes are not bit-for-bit reproducible. Every image records its
installed package versions at `/usr/local/share/wind-scale-packages.txt`;
the rootfs and minimeta VM also record their agent/binary checksums there.
Archive these manifests, image digests, and artifact hashes with validation
results for a particular deployment.

## Stage assets and deploy

```bash
python3 renewables/wind/wind-scale/fetch_weather.py
mkdir -p /phenix/injects/wind-scale
cp -R renewables/wind/wind-scale/phenix-injects/. /phenix/injects/wind-scale/
docker exec phenix phenix config create \
  /phenix/sceptre-phenix-topologies/renewables/wind/wind-scale/phenix-configs/topology.yml \
  /phenix/sceptre-phenix-topologies/renewables/wind/wind-scale/phenix-configs/scenario.yml
docker exec phenix phenix experiment create wind-scale \
  -t wind-scale -s wind-scale
docker exec phenix phenix experiment schedule wind-scale single-node
docker exec phenix phenix experiment start wind-scale
```

Scale generates `wtg-1`; do **not** retain the six hand-written turbine VMs
from the deprecated topology. `rootfs_source` and `replayData` are head-node
paths: Scale injects them into each generated VM. Containers mount their
generated XML/flow directory at `/etc/ot-sim` and replay data at `/shared`.
The rootfs is staged separately at `/scale/rootfs/otsimfs.tgz`, outside the
weather volume; containers do not receive the rootfs archive in `/shared`.
The `ot` VLAN is allocated by phēnix; nested minimega receives its numeric ID.

Increase `count` for more turbines. `containers_per_node` must be a positive
multiple of six so a turbine's private network never spans host VMs.
Addresses start at `192.168.100.10`; keep allocations below the Grafana address
`.250` (at most 240 turbines with this subnet/address plan).
Tune VM and container memory before scaling.

## Verify a live experiment

```bash
docker exec phenix phenix vm info wind-scale
docker exec minimega mm namespace wind-scale cc clients
docker exec minimega mm namespace wind-scale \
  cc tunnel grafana 30000 localhost 3000
docker exec minimega mm namespace wind-scale \
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

### Live acceptance checklist

Artifact tests do not verify nested networking. Before treating this example
as validated on a Linux deployment, record these checks and the versions used:

1. In `wtg-1`, verify `ip link show ens1`, `ovs-vsctl show`, and
   `mm namespace wind vm info`: the outer NIC belongs to the experiment trunk
   bridge and all six inner containers are running.
2. Compare `phenix vlan alias wind-scale ot` with
   `mm namespace wind vlans` inside `wtg-1`; the external VLAN's numeric ID
   must agree. Check the generated `.mm` script in the app's images directory.
3. Verify six inner miniccc clients and the controller IPv4 addresses.
   OT-sim must not start until addresses exist. Deliberately delay Elasticsearch
   on a test run: readiness diagnostics should appear, followed by normal
   startup once the cluster becomes ready. Leave it unavailable for 300 seconds
   on another test run: startup must fail explicitly without creating data.
4. From a private controller, verify reachability of `192.168.100.250:9200`
   through the main controller; inspect its IP forwarding and NAT rule.
5. Confirm `GET /_index_template/wind-turbine` exists before telemetry, then
   nonzero document counts and both Grafana panels without aggregation errors.
6. Record free disk space on `wtg-1` after rootfs injection/extraction and run
   for the intended replay duration; restart before the 42,000-row EOF.

These checks require an isolated Linux deployment. The repository tests cover
readiness success, delayed dependencies, and explicit timeout, not KVM,
Open vSwitch, NAT, disk capacity, or the full 11h40m replay.

Stop the lab when finished:

```bash
docker exec phenix phenix experiment stop wind-scale
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
PHENIX_LOG_FILE="" python -m pytest renewables/wind/wind-scale/tests
```

Use Python 3.12+ and adjust the companion checkout path if needed. The apps
repository keeps independent plugin regression tests and does not require this
topology checkout. These tests use the installed companion package.

This is not a live KVM/Elasticsearch/Grafana integration test. Image builds and
the live checks above must run on the target Linux deployment.
