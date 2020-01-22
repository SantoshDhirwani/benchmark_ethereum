#!/bin/sh

REPORTNAME=${1}

#ADD BIND AS REQUIREMENT OR WE MUST DO A MAKEFILE DOING THIS COMMAND AFTER INSTALLING
#pre-requisite installation
#curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
#sudo apt-get install -y nodejs
#npm install web3
#npm install --only=prod @hyperledger/caliper-cli
#npx caliper bind --caliper-bind-sut ethereum --caliper-bind-sdk 1.2.1 --caliper-cwd ./ --caliper-bind-args="-g"
npx caliper benchmark run \
    --caliper-workspace caliper-config \
    --caliper-benchconfig scenario/simple/config.yaml \
    --caliper-networkconfig networks/ethereum/1node-clique/ethereum.json \
    --caliper-report-path "../caliper-reports/${REPORTNAME}" \
|| { rm -r ../caliper-reports/${REPORTNAME}; exit 1; } #delete report and return exit code
