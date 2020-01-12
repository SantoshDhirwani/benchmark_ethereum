#!/bin/sh

#pre-requisite installation
curl -sL https://deb.nodesource.com/setup_13.x | sudo -E bash -
sudo apt-get install -y nodejs
npm install web3

#caliper part
npm install --only=prod @hyperledger/caliper-cli
npx caliper bind --caliper-bind-sut ethereum --caliper-bind-sdk 1.2.1 --caliper-cwd ./ --caliper-bind-args="-g"
npx caliper benchmark run --caliper-workspace ./config --caliper-benchconfig config.yaml --caliper-networkconfig network.json