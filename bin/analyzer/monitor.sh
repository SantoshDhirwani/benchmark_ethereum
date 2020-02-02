#!/usr/bin/env bash

set -e

export WS_SECRET=mysecret
sudo killall pm2 || true
sudo killall node || true

if [ ! -d "eth-netstats" ] ; then
    git clone https://github.com/cubedro/eth-netstats
    cd eth-netstats
    sudo npm install
    sudo npm install -g grunt-cli
    grunt
    cd ..
fi
cd eth-netstats
nohup npm start &
cd ..

if [ ! -d "eth-net-intelligence-api" ] ; then
    git clone https://github.com/cubedro/eth-net-intelligence-api
    cd eth-net-intelligence-api
    sudo npm install
    cd ..
fi

cd eth-net-intelligence-api
jsonStr=$(cat app.json)

COUNTER=0
for NODE in $(cat ../../run_caliper.conf)
do
    NODE_IP=$(echo ${NODE} | cut -d ":" -f1)
    echo ${NODE_IP}
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].name = "node-app"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].script = "app.js"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].log_date_format = "YYYY-MM-DD HH:mm Z"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].merge_logs = false')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].watch = "false"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].max_restarts = "10"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].exec_interpreter = "node"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].exec_mode = "fork_mode"')

    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].env.RPC_PORT = "8501"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].env.RPC_HOST = "'${NODE_IP}'"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].env.LISTENING_PORT = "30311"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].env.INSTANCE_NAME = "'${NODE_IP}'"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].env.WS_SERVER = "localhost:3000"')
    jsonStr=$(echo ${jsonStr} | jq '.['${COUNTER}'].env.WS_SECRET = "'${WS_SECRET}'"')
    ((COUNTER+=1))
done
pwd
rm -f app1.json
echo ${jsonStr} > app1.json

nohup pm2 start app1.json &