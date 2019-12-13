#!/bin/sh

npx caliper bind && npx caliper benchmark run \
 --caliper-workspace /hyperledger/caliper/workspace \
 --caliper-benchconfig config.yaml \
 --caliper-networkconfig network.json \
 --caliper-report-path ./report.html