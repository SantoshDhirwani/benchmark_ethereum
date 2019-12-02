#!/bin/sh

NETWORK_ID=$1

#create new key and init genesis
rm rf .ethereum/
geth --datadir .ethereum/ account new --password password
geth --datadir .ethereum/ init genesis.json

#get account
ACCOUNT=0x$(geth --datadir .ethereum/ account list | awk -F'[{|}]' '{print $2}')

#get bootnode
ENODE_BOOTNODE=$(cat bootnode)

#start the node
geth --datadir .ethereum/ --syncmode 'full' --port 30311 --rpc --rpcaddr '0.0.0.0' --rpcport 8501 --rpcapi 'personal,db,eth,net,web3,txpool,miner' --bootnodes ${ENODE_BOOTNODE} --networkid ${NETWORK_ID} --gasprice '1' -unlock ${ACCOUNT} --password password --allow-insecure-unlock --nousb