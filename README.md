# phenix-topologies

Topologies created to work with the latest version of [phenix](https://github.com/sandialabs/sceptre-phenix).

## Usage

Install [Git LFS](https://git-lfs.com/):

```shell
sudo apt install -y git-lfs
git lfs install
```

Then clone the repository, including LFS-tracked files:
```shell
git clone https://github.com/sandialabs/sceptre-phenix-topologies.git
cd sceptre-phenix-topologies
git lfs pull
```

You're now ready to create experiments! A good starting place is the [soap topology](https://github.com/sandialabs/sceptre-phenix-topologies/tree/main/soap), which has a detailed example.

Here's a simple "hello world", assuming you have phenix setup:

```shell
cp -r ./helloworld /phenix/topologies/.
phenix experiment create hello-world -t /phenix/topologies/helloworld/helloworld.yaml
phenix experiment start hello-world
```

## Topologies

- Wind Architecture. Four [topologies](renewables/wind/plant) are included for a representative wind plant architecture, and also a [turbine](renewables/wind/turbine) topology.
- [helloworld](./helloworld) - A basic example topology.
- [soap](./soap) - Complete example topology demonstrating the Hardware-In-the-Loop (HIL) capabilities of SCEPTRE.
- [soap-legacy](./soap-legacy) - The SOAP topology models a notional SCADA system for a 300 bus microgrid system.
- [waterway](./waterway) - The waterway topology models a notional SCADA system for a waterway lock system.
