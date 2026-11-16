# mitm-arm64

The arm64, all-Linux counterpart of [mitm](../mitm) (PR #31): a lean waterway derivative for ARP man-in-the-middle testing on the ICS segment. Both are published: `mitm` is the original x86 topology (Windows `opc.qc2`, `bennu.qc2`, `kali.qc2`); `mitm-arm64` keeps the same node set, names, addressing and attack and swaps in the arm64 images from [waterway-arm64](../waterway-arm64), including a Linux OPC UA gateway in place of the Windows OPC server. It adds an optional blue-team node.

## Nodes

| Host | Image | Address | Role |
| --- | --- | --- | --- |
| `simulink-provider` | bennu-arm64.qc2 | MGMT 172.16.1.2 | Simulink provider driving ferrofire (`ferrofire-simulinksolver`) |
| `opc` | opc-arm64.qc2 | SCADA 10.1.2.50 | Modbus master polling rtu-1/rtu-2, OPC UA server |
| `rtu-1`, `rtu-2` | bennu-arm64.qc2 | ICS 10.1.1.101 / .102 | SCEPTRE RTUs (Modbus 502) |
| `router` | minirouter-arm64.qc2 | ICS 10.1.1.1 | ICS/SCADA/MGMT router |
| `kali` | kali-arm64.qc2 | ICS 10.1.1.200 | attacker; ettercap |
| `blue` | kali-purple-arm64.qc2 | MGMT 172.16.1.250, second NIC `capture` on VLAN `MIRROR` (placeholder 192.0.2.250/24; phenix requires an address) | Kali Purple + Malcolm (Zeek, Suricata, Arkime); optional |

Delete the `blue` node from `mitm-topology.yaml` if you do not have that image (it needs 24 GiB and an 80 GiB disk). Its capture NIC (eth1) only sees traffic if you mirror the experiment's OVS ports to it, for example with an `ovs-vsctl` mirror on the `phenix` bridge selecting the ICS/SCADA taps and outputting to blue's second tap.

## Attack

`mitm-scenario.yaml` has the `sceptre` app plus a `scorch` app with two components and two runs:

- `ettercap` on `kali` (`iface: eth0`, the guest's NIC name; `IF0` is only phenix's label): `ettercap -Tq -i eth0 -M arp /10.1.1.101// /10.1.1.1//`, poisoning `rtu-1` <-> `router`.
- `mitm-capture`: tcpdump on `kali`, `tcp port 502`.
- run `mitm-start` starts both, `mitm-stop` stops them, so the attack can be observed in between.

```
cp -r mitm-arm64 /phenix/topologies/.
phenix config create /phenix/topologies/mitm-arm64/mitm-topology.yaml
phenix config create /phenix/topologies/mitm-arm64/mitm-scenario.yaml
phenix exp create mitm -t mitm-arm64 -s mitm-arm64
phenix exp start mitm
phenix experiment scorch mitm -r 0     # mitm-start
phenix experiment scorch mitm -r 1     # mitm-stop, collects the pcap
```

## Relationship to PR #31 (`mitm`)

Same experiment, different guests; use `mitm` on x86 hosts and `mitm-arm64` on arm64 hosts. Differences: the arm64 node block described in [waterway-arm64](../waterway-arm64/README.md), a Linux `opc`, the `scorch` ettercap/tcpdump components already wired into the scenario, and the optional `blue` node. This directory has no dependency on the `mitm/` checkout.

## Prerequisites

Same as [waterway-arm64](../waterway-arm64/README.md#prerequisites), plus `kali-arm64.qc2` (and `kali-purple-arm64.qc2` for `blue`) built with the range repository's recipes, and ferrofire's solver copied to `/phenix/topologies/mitm-arm64/injects/ferrofire-simulinksolver` (not included, not MATLAB/Simulink; see that README).
