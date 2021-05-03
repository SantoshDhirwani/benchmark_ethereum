# Cloud Prototyping 2019/2020



## A benchmarking-based approach to maximise throughput of the private Ethereum


Our goals were to achieve :
1) Performance Benchmarking. Benchmarking the performance of private Ethereum with Proof-of-Authority consensus  while maximising throughput depending on block size and block interval.
2) Automation. Scaling dynamically the SUT and to derive and present a few high-level guidelines reducing the complexity of implementing and running blockchain benchmarking performance, which would be valuable to developers and deployment engineers.


## Our repository
```
.
├── bin
│   ├── main.py
│   ├── sut
│   │   ├── deploy-sut.sh
│   │   ├── startup-script.sh
│   │   ├── create-template-multi-region.sh
│   │   └── create-template.sh
│   │  
│   ├── workload
│   │   ├── caliper-config/
│   │   ├── caliper-reports/
│   │   ├── run-caliper.py
│   │   └── run-caliper.sh
│   │  
│   └── analyzer
│       ├── old/
│       ├── aggregated-results/
│       ├── aggregate-html-reports.py
│       ├── backup-old-results.py
│       ├── calculate-optimal-values.py
|       ├── dashboard.html
|       ├── monitor.sh
│       └── get-last-throughput
|
│── config
│      └── config.json
│
├── Docker
│   ├── bootnode
│   │   ├── boot.key
│   │   ├── Dockerfile
│   │   ├── init-bootnode.sh
│   │   ├── karim-harmony.json
│   │   └── karim.json
│   ├── ether-node
│   │   ├── bootnode
│   │   ├── Dockerfile
│   │   ├── genesis.json
│   │   ├── init-ether.sh
│   │   └── password
│   └── sealer-node
│       ├── bootnode
│       ├── Dockerfile
│       ├── init-sealer.sh
│       └── password
│
│──  documentation
└──README.md


```



## Getting started

Get a copy of the project and run it up on your local machine for development and testing purposes.

`git clone https://github.com/Cloud-Prototyping-WS-2019-20/cp_ws_1920.git`


## Prerequisites

The script checks if the needed dependencies are installed or how to install them. It also runs the script  create-template.sh  to create VM templates.

**Run:**  `sh prerequisites.sh`


**Dependency**
- Python 3 libraries : pandas, lxml, matplotlib, numpy
- web3: 1.2.6 (it works from 1.2.0 version)
- pm2: 4.2.3
- Google SDK
- Geth
- Puppeth
- jq-command : https://stedolan.github.io/jq/
- npm (Node.js) : https://nodejs.org/en/download/ - to run caliper a bigger version - than Node.js v8.X LTS  is needed
- Caliper : https://hyperledger.github.io/caliper/vLatest/installing-caliper/

Note: If you have jq,npm, geth, puppeth and gcloud not installed, you will be provided with the links to follow the easy steps of installing them. This script does not provide their installation, because each user have different OS, and you need to download and install the packages depending on the environment you are working from.


## Executing the tool

`cd cp_ws_1920/bin`

`python main.py`

**Flags**

`--verbose` is the verbose levels. We have defined 3 verbose levels: 0,1 and 2, where '0' will print only the result, '1' will print the execution steps and '2' will print everything (recommended for debugging).

`--notbuildsut` when enabled the sut will not be built (or rebuilt) Google Cloud project setup.

`--monitor` enables ethstats monitoring

**Reports**

To check final report of benchmarking open dashboard.html in folder bin/analyzer/aggregated-results

## Config

config.json is where the user configuration parameters are written.

**The values of "tool_config" are all needed to run the main.py.**

- "maxGas" sets the maximal block gas limit value. If this value is reached by our tool when trying to find the minimum block gas limit, it will stop and throw an error.

- "minGas" sets the minimum block gas limit value with which the tool starts benchmarking.

- "defaultGas" sets a working block gas limit value with which our tool will benchmark to find the minimum block interval.

- "gasStep" the block gas limit step difference of the tool. It will be added to the last block gas limit value benchmarked.

- "gasLimitAccuracy" the maximum difference value between the lower bound and upper bound block gas limit values when searching for the minimum block gas limit of a given block interval.

- "maxInterval" the maximum block interval value. When our tool is searching for the minimum block interval value stops and throws an error if this configuration value is reached

- "minInterval" the maximum block interval value with which our tool will start benchmarking to find the minimum block interval value.

- "intervalStep" the block interval step difference of the tool. It will be added to the last block interval value benchmarked.

- "numberTrials" the minimum number of successful benchmarks needed to find a peak.

- "sensitivity" percentage value of the minimum improvement difference between successful benchmarks accepted by the user. If an improvement of less percentage than the configured is obtained, the tool will stop the execution and assume that the throughput value is stale.

**Under "sut_config" we have parameters needed to build the SUT:**

- "templateName", is the name of the template that will be used to create the VM instances of the SUT.

- "nodeNumber", the number of nodes to build the SUT and to deploy a private Ethereum network on Google Cloud Platform. The SUT infrastructure will be deployed in the default region of the user configured in Google SDK.

- "nodes", a configuration array of nodes to build a multi-region SUT. Each node must have a Region and a Zone. If this configuration is present, the tool will ignore the "nodeNumber" value.

**Under"workload_config" we have .**
- "attempt" sets the max attempts to run caliper in our case.

**Under "eth_config" we have Ethereum sut configuration.**
- "username" used to access via SSH to the VMs.
- "password used" to access via SSH to the VMs.
- "network_id" the network id used to configure the Ethereum network.

## Documentation
This file serves the user to have a more in depth-learning of this tool and how it was organised and developed by the team.


## Docker
For future work, we can run in Docker.
We import from [ethereum/client-go:alltools-stable](https://hub.docker.com/r/ethereum/client-go)  as it has most of the tools we need.

So far we have three images:

### Bootnode Image
In oder to achieve loose coupling among the nodes we need to start a bootnode which will take the boot.key as input and will listen to port 3031

### Ethereum Node Image
Takes for input the genesis file and bootnode (just paste address in the bootnode file) and start a node on the default port. You don't need to create an account for this node as it fully automated within the image.

### Sealer Node Image
Takes for input the genesis file and bootnode (just add the address in the bootnode file) and start a mining node that could seal on the default port. It also generated the genesis file accordingly. As Sealers should be in the genesis.json.

## Visitors Counts

![Visitor Count](https://profile-counter.glitch.me/benchmark_ethereum/count.svg)
