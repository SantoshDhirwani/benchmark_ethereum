#!/usr/bin/env bash

set -e

if [ ! -d "eth-netstats" ] ; then
    git clone https://github.com/cubedro/eth-netstats
    cd eth-netstats
    sudo npm install
    sudo npm install -g grunt-cli
    grunt
    cd ..
fi
nohup npm start eth-netstats/app.js &


if [ ! -d "eth-net-intelligence-api" ] ; then
    git clone https://github.com/cubedro/eth-net-intelligence-api
    cd eth-net-intelligence-api
    sudo npm install
    sudo npm install -g pm2
    cd ..
fi

jsonStr=$(cat eth-net-intelligence-api/app.json)
IP_NODE=$(head -1 run_caliper.conf | cut -d ":" -f1)
echo ${IP_NODE}

jsonStr=$(echo ${jsonStr} | jq '.[0].env.RPC_PORT = "123"')
jsonStr=$(echo ${jsonStr} | jq '.[0].env.RPC_HOST = "'${IP_NODE}'"')
jsonStr=$(echo ${jsonStr} | jq '.[0].env.LISTENING_PORT = "30311"')
jsonStr=$(echo ${jsonStr} | jq '.[0].env.INSTANCE_NAME = "Geth/v1.9.8-stable-d62e9b28/linux-amd64/go1.13.4"')
jsonStr=$(echo ${jsonStr} | jq '.[0].env.WS_SERVER = "locaholst:3000"')
jsonStr=$(echo ${jsonStr} | jq '.[0].env.WS_SECRET = "mysecret"')

rm -f eth-net-intelligence-api/app.json
echo ${jsonStr} > eth-net-intelligence-api/app1.json

nohup pm2 start eth-net-intelligence-api/app.json &