The helloworld topology models a simple 2 VM topology as an introductory example.  

The model consists of the following configurations: 
- `helloworld-topology.yaml` - This defines the network topology for the CF19 model.

The model uses the following backing images:
- `ubuntu.qc2` - the ubuntu image can be built using `phenix image` with the following commands:
    ```
    phenix image create /phenix/vmdb2/scripts/ubuntu --format qcow2 --release focal -c ubuntu
    phenix image build ubuntu -o /phenix -c -x
    ```

To run the model use the following commands
```
phenix config create <path_to_topos>/helloworld.yaml
phenix exp create helloworld -t helloworld
```
