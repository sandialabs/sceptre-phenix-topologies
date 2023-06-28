# Wind Turbine

## Background

This wind turbine model was created as part of the Department of Energy (DOE)
Wind Energy Technology Office (WETO) funded "Wind Reference Architecture"
project at DOE's National Renewable Energy Laboratory (NREL). It leverages
[OT-sim](https://github.com/patsec/ot-sim), and included the development of two
new OT-sim modules
([wind_turbine/anemometer](https://github.com/patsec/ot-sim/tree/main/src/python/otsim/wind_turbine/anemometer)
and
[wind_turbine/power_output](https://github.com/patsec/ot-sim/tree/main/src/python/otsim/wind_turbine/power_output))
and a new phenix user app
([wind-turbine](https://github.com/sandia-minimega/phenix-apps/tree/main/src/python/phenix_apps/apps/wind_turbine)).

## Deploying in phēnix

A wind turbine experiment has been designed to be deployed using
[phēnix](https://github.com/sandia-minimega/phenix). The easiest way to deploy
phēnix is to use the Docker Compose configs present in the `docker` directory of
the phēnix repository.

The phēnix configs in this repository include file injection references to
`/phenix/injects/wind-turbine`. To ensure these injections work correctly, users
need to copy the contents of `phenix-injects` to `/phenix/injects/wind-turbine`
on the server where phēnix is running (the "head node").

```
mkdir -p /phenix/injects/wind-turbine
cp -a phenix-injects/* /phenix/injects/wind-turbine
```

The phēnix topology config in this repository include VM disk references to
`ot-sim.qc2` and `grafana.qc2`. phēnix image configs for `ot-sim` and `grafana`
are included in this repository in the `phenix-images` directory and can be
built with the `phenix image build` command. First, add the image configs to
phenix either via the command line or the UI. Then, run the following commands
to build the images.

```
phenix image build -x -c -o /phenix/vmdb ot-sim
phenix image build -x -c -o /phenix/vmdb grafana
```

Once built, be sure to also configure the images to boot with minimega's
`miniccc` agent using the `phenix image inject-miniexe` command.

```
phenix image inject-miniexe /opt/minimega/bin/miniccc /phenix/vmdb/ot-sim.qc2
phenix image inject-miniexe /opt/minimega/bin/miniccc /phenix/vmdb/grafana.qc2
```

Then, move the image files to the `/phenix/images` directory so phenix and
minimega know where to grab them from.

To create an experiment, add the topology and scenario file from
`phenix-configs` to the phēnix store either via the command line or the UI.
Next, create an experiment in the phēnix UI by referring to the appropriate
topology and scenario for the given network above.

Once you start the experiment, you can verify it is operating as expected by
checking the Grafana dashboard. To access the grafana dashboard, you will need
to use minimega's port forwarding capability since there are no VMs in this
experiment with operating systems that include a browser.

```
docker exec -it minimega /opt/minimega/bin/minimega -e \
  cc tunnel grafana 30000 localhost 3000
```

Then, from your local computer, browse to http://localhost:30000 to access the
Grafana dashboard.
