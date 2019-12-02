#!/bin/sh

NETWORK_ID=$1

rm rf .ethereum/ genesis.json

# create new key
geth --datadir .ethereum/ account new --password password

# build genesis
printf "2\n1\n2\n15\n${ACCOUNT}\n\n${ACCOUNT}\n\nyes\n${NETWORK_ID}\n2\n2\n\n" | puppeth --network genesis

# init genesis
geth --datadir .ethereum/ init genesis.json

#get account
ACCOUNT=0x$(geth --datadir .ethereum/ account list | awk -F'[{|}]' '{print $2}')

#get bootnode
ENODE_BOOTNODE=$(cat bootnode)

#start the node
geth --datadir .ethereum/ --syncmode 'full' --port 30311 --rpc --rpcaddr '0.0.0.0' --rpcport 8501 --rpcapi 'personal,db,eth,net,web3,txpool,miner' --bootnodes ${ENODE_BOOTNODE} --networkid ${NETWORK_ID} --gasprice '1' -unlock ${ACCOUNT} --password password --allow-insecure-unlock --nousb --mine