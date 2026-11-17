# waterway-arm64

The [waterway](../waterway) lock model on an arm64 host (for example an Apple Silicon Mac running Linux KVM guests under nested virtualization), with the Windows SCADA stack replaced by Linux software. The physics, RTUs, router and addressing are the same as `waterway`; everything is static YAML plus injects, nothing is generated at run time.

## What differs from `waterway`

### Node block

Every VM uses an aarch64 `virt` machine instead of the x86 defaults phenix writes:

```yaml
hardware:
  cpu: host                     # phenix default (Broadwell) is invalid on aarch64
  drives:
  - image: <name>-arm64.qc2
    interface: virtio
    inject_partition: 2         # images are GPT with an ESP; the root fs is partition 2
advanced:
  machine: virt
  vga: virtio
  qemu-append: -bios /usr/share/AAVMF/AAVMF_CODE.fd   # UEFI firmware; replaces phenix's "-vga qxl"
overrides:
  bus=usb-bus.0: bus=xhci.0     # minimega's usb-tablet device names the x86-only usb-bus.0
```

GUI nodes (`hmi`, `engineer-workstation`) append `-device virtio-gpu-pci -device usb-kbd,bus=xhci.0` to `qemu-append`: `virt` has no VGA, so without a GPU the console is black and has no keyboard.

### Linux replacements for the Windows roles

| Host | Original | Here | Image |
| --- | --- | --- | --- |
| `waterway-provider` | bennu + x86 `simulinksolver` | bennu-simulink-provider + ferrofire (`ferrofire-simulinksolver`) | `bennu-arm64.qc2` |
| `rtu-1`, `rtu-2` | bennu field device | same, native arm64 build; `rtu-1` also carries a `boat` device | `bennu-arm64.qc2` |
| `opc` | Kepware OPC TOP Server | Python gateway: Modbus master (pymodbus) -> OPC UA server on `10.1.2.50:4840` (asyncua), configured by `injects/opc_gateway.json` | `opc-arm64.qc2` |
| `historian` | Wonderware | InfluxDB 2 + Telegraf (OPC UA input), `injects/telegraf.conf`, `injects/influx-setup.sh` | `historian-arm64.qc2` |
| `scada-server` | mySCADA | FUXA with an OPC UA client device, `injects/fuxa_project.json` (HTTP 1881) | `scada-arm64.qc2` |
| `hmi` | Win7 mySCADA HMI | xfce autologin, Firefox kiosk on `http://10.1.2.71:1881/` | `hmi-arm64.qc2` |
| `engineer-workstation` | Win7 | xfce plus brash terminals; `injects/rtus.txt` lists the RTUs | `engineer-arm64.qc2` |
| `router` | minirouter | same | `minirouter-arm64.qc2` |

## Prerequisites

- An arm64 host with KVM, minimega with `qemu-system-aarch64` and the AAVMF firmware (`/usr/share/AAVMF/AAVMF_CODE.fd`), and a phenix that supports the `advanced`, `overrides` and `inject_partition` node fields.
- minimega starts guests with `-vga <type>`, which `virt` ignores. The `advanced.qemu-append` above works around that for GUI nodes; the `kvm` binary minimega runs also needs to be a `qemu-system-aarch64` launcher that supplies `-M virt` (aarch64 has no default machine).
- The images in the table. This repository has no arm64 recipes yet; they were built with the recipes of the [phenix-waterway-range](https://github.com/adamsrnmsu/phenix-waterway-range) repository (`images/recipes/*.env`, `images/build.sh <name>`).
- `injects/ferrofire-simulinksolver`: [ferrofire](https://github.com/adamsrnmsu/ferrofire)'s Simulink-compatible solver, NOT included here (it is a binary). It is not built from MATLAB/Simulink: it is a Rust reimplementation of the waterway lock model that talks to the stock `bennu-simulink-provider` over the same shared-memory and semaphore interface as the Simulink-generated `simulinksolver` in `waterway/`. Build it with ferrofire's `build-linux.sh` (glibc aarch64; outputs `dist/simulinksolver`) and copy that to `/phenix/topologies/waterway-arm64/injects/ferrofire-simulinksolver`; `waterway-scenario.yaml` points the provider at it. Keep a name ending in `simulinksolver`: the ferrofire binary picks its solver mode from its file name. With no `--model` it runs its built-in waterway model.

## Run

The YAML paths assume the directory is installed at `/phenix/topologies/waterway-arm64`:

```
cp -r waterway-arm64 /phenix/topologies/.
phenix config create /phenix/topologies/waterway-arm64/waterway-topology.yaml
phenix config create /phenix/topologies/waterway-arm64/waterway-scenario.yaml
phenix exp create waterway-arm64 -t waterway-arm64 -s waterway-arm64
phenix exp start waterway-arm64
```

The HMI is served on `http://10.1.2.71:1881/` (SCADA VLAN) and shown full-screen on the `hmi` VM.

## Notes

- Lab defaults only: InfluxDB admin password `waterway-admin-pass`, token `waterway-historian-token` (`injects/influx-setup.sh`, `injects/telegraf.conf`).
- Addressing matches `waterway`: ICS `10.1.1.0/24`, SCADA `10.1.2.0/24`, MGMT `172.16.0.0/16`.
