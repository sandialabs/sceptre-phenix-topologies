The helloworld topology models a simple 2 VM topology as an introductory example.  

The model consists of the following configurations: 
- `helloworld.yaml` - This defines the network topology for the helloworld model.

The model uses the following backing images:
- `ubuntu.qc2` - available from [sceptre-phenix-images](https://github.com/sandialabs/sceptre-phenix-images) 

To download `ubuntu.qc2`, install [ORAS](https://oras.land/docs/installation/), then run:

```shell
cd /phenix/images/
oras pull ghcr.io/sandialabs/sceptre-phenix-images/ubuntu.qc2:latest
```

> ![NOTE]
> These examples assume the [sceptre-phenix-topologies](https://github.com/sandialabs/sceptre-phenix-topologies/) git repository has been cloned into `/phenix/topologies/` or the files have been manually copied into `/phenix/topologies/`.
> For example: `git clone https://github.com/sandialabs/sceptre-phenix-topologies/ /phenix/topologies && cd /phenix/topologies/ && git lfs pull`


To run the helloworld model, use the following commands:
```shell
phenix experiment create hello-world -t /phenix/topologies/helloworld/helloworld.yaml
phenix experiment start hello-world

# To stop:
phenix experiment stop hello-world
```


Alternative way to demonstrate use of configs. `phenix config create` creates the Topology config in the phenix database, then `phenix experiment create` creates a phenix Experiment, referencing the `helloworld` Topology from the phenix database.

```shell
phenix config create /phenix/topologies/helloworld/helloworld.yaml
phenix experiment create hello-world -t helloworld
phenix experiment start hello-world

# To stop:
phenix experiment stop hello-world
```