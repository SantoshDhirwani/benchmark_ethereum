#!/bin/sh

cd ~
cd hyperledger/caliper-workspace
npx caliper bind --caliper-bind-sut ethereum --caliper-bind-sdk 1.2.1 --caliper-cwd ./ --caliper-bind-args="-g"
npx caliper benchmark run --caliper-workspace /hyperledger/caliper-workspace --caliper-benchconfig config.yaml --caliper-networkconfig network.json