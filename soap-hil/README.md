This repository contains a topology to demonstrate the Hardware-In-the-Loop (HIL) capabilities of SCEPTRE. The topology is based on the original SOAP (SCEPTRE on a Platter) topology and underlying power model, simulated using PyPower. It includes the integration of a Siemens S7 PLC as HIL, functioning as a simple controller in the power model. This topology also still fully functions without HIL and can be used by selecting a second, "virtual only" control screen on the HMI.

In addition to the topology, this repo includes a demo attack against the PLC to manipulate and destablize the power system model.

# Getting Started
Most of the software components of this SCEPTRE topology are contained in this repository, so `git clone` is sufficient to get them.


## Hardware
The Siemens PLC can be purchased in a kit from [PLCCable.com](https://plccable.com/). 
[This kit](https://www.plccable.com/siemens-s7-1200-deluxe-plc-trainer-analog-no-software-ethernet-1215/) has the appropriate PLC and analog output modules. Please note that these instructions were made with the S7-1214 and the latest version of the kit uses an S7-1215, which may require some tweaking.  
You can also purchase the Siemens TIA software for programming the PLC [here](https://www.plccable.com/siemens-6es7822-0aa08-0ya5-tia-portal-s7-v18-basic-plc-programming-software/)

The LabJack T4 can be purchased directly from [the manufacturer](https://labjack.com/).
Here is a direct link: https://labjack.com/products/labjack-t4.

Since the LabJack can only drive digital outputs from 0-5V, a 12V relay is used to drive the PLC digital inputs.
A suitable relay can be purchased from Mouser [here](https://www.mouser.com/ProductDetail/Parallax/27115?qs=uPOdrd2%252BfdKcmDw43c3OZA%3D%3D).

Additionally, some wires will be needed to wire the LabJack to the PLC.
A wire kit can be found on Amazon.com [here](https://www.amazon.com/AWG-Stranded-Wire-Kit-Pre-Tinned/dp/B07T4SYVYG)

The following steps will setup the hardware correctly:

* Follow `WIRING.md` to setup the PLC and LabJack.
* Program the PLC with the project contained in the `satx-plc-program.zip` archive.
* Connect the Ethernet port on the PLC to the `eno4` interface of the SCEPTRE host.
    * Other interfaces will also work, but the `hil_network.sh` script will need to be modified accordingly.


## Phenix & Minimega
Follow the instructions at https://phenix.sceptre.dev/latest for installing `phenix`.
Additional documentation on using `phenix` can be found at https://sandialabs.github.io/sceptre-docs.


## Creating the SCEPTRE images.
Now that phenix & minimega are ready to go, it is time to prepare the Ignition, bennu, and kali images.

### Ignition
#### Getting Ignition
Grab the Ignition 8.0.6 Linux 64-bit zip from https://inductiveautomation.com/downloads/archive/8.0.6  
(You will have to sign up for a free Inductive Automation account)

#### Base image
Load the image config from this repo with the following command

```bash
phenix config create /phenix/topologies/soap-hil/image-configs/Image-ignition.yml
```

Build the image with

```bash
phenix image build ignition -c -x -o /phenix/images
```

Install the miniccc binary and service in the image
```bash
phenix image inject-miniexe /phenix/miniccc /phenix/images/ignition.qc2
```

Copy the ignition installer to the new disk image
```bash
mm disk inject ignition.qc2 files <ignition_installer>:/root
```

Use the following to boot the image and connect to it with minimega:  
_note that this boots the image directly (no snapshots) so that we can install ignition persistently in the qc2_

```bash
#!/bin/bash

NAMESPACE=minimega
NAME=test
SNAPSHOT=false # used in order to do base image setup
DISK=/phenix/images/ignition.qc2
MM="docker exec -it minimega minimega -e namespace $NAMESPACE

set -e
set -x
$MM namespace $NAMESPACE
$MM clear vm config
$MM vm config cpu host
$MM vm config memory 8192
$MM vm config net 500
$MM vm config vcpus 4
$MM vm config snapshot $SNAPSHOT
$MM vm config disk $DISK
$MM vm config qemu-append -vga qxl
$MM vm launch kvm $NAME
$MM vm start $NAME
```

Run the ignitions installer in the VM in the `/root` directory, making sure to add the ignition install folder (typically `/usr/local/bin`) to `$PATH` for all users.
Additionally, open a web browser (in the virtual machine), navigate to localhost:8088 and download and install the Designer Launcher.

### Bennu
[Bennu](https://github.com/sandialabs/sceptre-bennu) is a modeling and simulation application for ICS/SCADA devices.
The instructions at [https://github.com/sandialabs/sceptre-phenix-images] are sufficient to build a vm image containing bennu.
This image should be placed at `/phenix/images/bennu.qc2`

### Kali
`phenix` includes a configuration for kali, which we will modify by installing the `python3-snap7` library used by one of the attacker scripts.

First, load the image config from this repo
```bash
phenix config create /phenix/topologies/soap-hil/image-configs/Image-kali-python.yml
```

And build the updated image
```bash
phenix image build kali-python -c -x -o /phenix/images
```
Install the miniccc binary and service in the image
```bash
phenix image inject-miniexe /phenix/miniccc /phenix/images/kali-python.qc2
```

## Running the experiment

### HIL network setup
After completing all other steps, enter the topology directory and run `./expctl hil-network`.
This will setup minimega and the host so that the hardware can connect to the experiment.
_Note that you will need to update the interface name in this script to match the interface on your physical host where the PLC is connected._

### `expctl`
The `expctl` script provides helper functions for starting and stopping the experiment, as well as refreshing when modified and adding a network tap to the host.
To start the experiment, run `./expctl start`, which will also refresh the experiment if it is already started.
To stop the experiment, run `./expctl stop`.
To create a network tap on the host that is connected to the experiment network, run `./expctl tap`.

### Running the attack
A sample 'attack' is implemented in the `plc-attack.py` script injected into the `kali` machine.
After launching the experiment, enter the `kali` machine and navigate to `/phenix/`.
The script is runnable with
```bash
python3 plc-attack.py <STARTUP_DELAY_SECONDS> <NUMBER_REPEATS>
```

### Is it working?
To make sure everything is working properly, enter the `ignition` machine and open the `Designer Launcher` application.
Login with the username/password chosen when installing Ignition, open the `satx` project, and open the `Main Window` view.
Make this window fullscreen by pressing `F11` (You may need to enter the username/password again).

You should see a screen that looks like this:
![Ignition normally](img/ignition-normal.png)

Then run the attack as described above.
The output of the attack should be similar to what is seen in the following image
![Attack output](img/kali.png)

Navigate back to `ignition`.
The screen should now look like this:
![Ignition blacked out](img/ignition-blackout.png)


## Network Diagram
Here's a nice diagram of the machines in the experiment:
![Diagram](img/network.svg)

The yellow cloud is the EXP VLAN, and machines inside the cloud have their ipv4 addresses displayed.
Machines outside the cloud are not connected to the EXP VLAN, and communicate with the others over the MGMT VLAN instead.
The MGMT VLAN is not shown, but machine addresses can be seen in the `topology.yaml` file.
