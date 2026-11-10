# mitm

A lean waterway derivative for testing a man-in-the-middle attack on the ICS
segment, isolated from the full `waterway` topology so a MITM run does not
disturb the SCADA boards that share waterway.

## Nodes

| Host | Image | ICS (10.1.1.0/24) | Role |
| --- | --- | --- | --- |
| `simulink-provider` | bennu.qc2 | — (MGMT) | Simulink fuel provider |
| `opc` | opc.qc2 | — (SCADA) | OPC server, Modbus master polling rtu-1/rtu-2 |
| `rtu-1` | bennu.qc2 | 10.1.1.101 | SCEPTRE RTU (fd-server, Modbus 502) |
| `rtu-2` | bennu.qc2 | 10.1.1.102 | SCEPTRE RTU (fd-server, Modbus 502) |
| `router` | minirouter.qc2 | 10.1.1.1 | ICS/SCADA/MGMT router |
| `kali` | kali.qc2 | 10.1.1.200 | attacker; runs ettercap |

The Windows HMI/historian/SCADA/engineer-workstation VMs and their injects are
dropped from waterway: the OPC server alone drives the Modbus traffic a MITM
intercepts, which keeps the topology small.

## MITM

`kali` sits on the ICS segment with rtu-1, rtu-2 and the router, so it can ARP
man-in-the-middle any pair of them (for example rtu-1 and the router, to sit on
the OPC server's Modbus polls to rtu-1). The ettercap SCORCH component drives
the attack; the [everything-burger](https://github.com/adamsrnmsu/everything-burger)
`ettercap` switchboard runs it and verifies the interception.

Derived from `waterway`; the Simulink provider injects are copied verbatim.
