# Cloud Prototyping 2019/2020

## Motivation

This repository was created to automate the benchmarking process of ethereum with caliper. We have created the following docker images and automation scripts to make the process portable and repeatable as possible.

## Docker

we import from [ethereum/client-go:alltools-stable](https://hub.docker.com/r/ethereum/client-go)  as it has most of the tools we need.

So far we have three images:

```
.
├── Docker
│   ├── bootnode
│   │   ├── boot.key
│   │   ├── Dockerfile
│   │   ├── init-bootnode.sh
│   │   ├── karim-harmony.json
│   │   └── karim.json
│   ├── ether-node
│   │   ├── bootnode
│   │   ├── Dockerfile
│   │   ├── genesis.json
│   │   ├── init-ether.sh
│   │   └── password
│   └── sealer-node
│       ├── bootnode
│       ├── Dockerfile
│       ├── init-sealer.sh
│       └── password
└── README.md
```

### Bootnode Image
In oder to achieve loose coupling among the nodes we need to start a bootnode which will take the boot.key as input and will listen to port 3031

### Ethereum Node Image
Takes for input the genesis file and bootnode (just paste address in the bootnode file) and start a node on the default port. You don't need to create an account for this node as it fully autoamted withing the image.

### Sealer Node Image
Takes for input the genesis file and bootnode (just paste address in the bootnode file) and start a mining node that could seal on the default port. It also generated the genesis file accordingly. As Sealers should be in the genesis.json.
