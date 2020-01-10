#!/usr/bin/env bash
#Deploy SUT script
# ./deploy-sut.sh <number of nodes> <block interval> <block size>

NUMBER_NODES=${1}
BLOCK_INTERVAL=${2}
BLOCK_SIZE=${3}
INSTANCE_GROUP_NAME=ethereum-sut-group
BOOT_NODE_NAME=bootnode
INSTANCE_TEMPLATE=ethereum-sut-template

NETWORK_ID=123

# clean previous sut
echo deleting previous setup this might take some time...
echo
echo | gcloud compute instance-groups managed delete ${INSTANCE_GROUP_NAME}
echo | gcloud compute instances delete ${BOOT_NODE_NAME}

# run bootnode
gcloud compute instances create ${BOOT_NODE_NAME} --source-instance-template ${INSTANCE_TEMPLATE}
echo sleeping for 60 seconds to make sure bootnode is up!
sleep 60

IP_BOOTNODE=$(gcloud compute instances list --filter="name~${BOOT_NODE_NAME}" --format='value(INTERNAL_IP)')
gcloud compute ssh ${BOOT_NODE_NAME} --command "nohup bootnode -genkey boot.key && bootnode -nodekey boot.key -addr ${IP_BOOTNODE}:30310  &"
key=$(gcloud compute ssh ${BOOT_NODE_NAME} --command "cat boot.key")
hex=$(gcloud compute ssh ${BOOT_NODE_NAME} --command "nohup bootnode -nodekeyhex $key -writeaddress")
BOOTNODE_ENODE=enode://${hex}@${IP_BOOTNODE}?discport=30310
echo $BOOTNODE_ENODE

echo the boot node enode adress is: ${BOOTNODE_ENODE}

# create instance group of sealer nodes

gcloud compute instance-groups managed create ${INSTANCE_GROUP_NAME} \
   --base-instance-name ethereum-sut \
   --size ${NUMBER_NODES} \
   --template ${INSTANCE_TEMPLATE}

echo sleeping for 60 seconds to make sure instances are up!
sleep 60

prefix=$(gcloud compute instance-groups managed list --format='value(baseInstanceName)' --filter='name~^'${INSTANCE_GROUP_NAME}'')
INSTANCE_LIST=( $(gcloud compute instances list --filter="name~^${prefix}" --format='value(name)') )
ACCOUNT_LIST=()

# create accounts on nodes

for index in ${!INSTANCE_LIST[@]}; do
    echo creating geth account on ${INSTANCE_LIST[index]}
    gcloud compute ssh ${INSTANCE_LIST[index]} --command "echo password >> password && geth --datadir .ethereum/ account new --password password"
    ACCOUNT=$(gcloud compute ssh ${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ account list | cut -d "{" -f2 | cut -d "}" -f1")
    ACCOUNT_LIST[index]=${ACCOUNT}
done

ACCOUNT_STRING=""

for index in ${!ACCOUNT_LIST[@]}; do
    ACCOUNT_STRING+="${ACCOUNT_LIST[index]}\\n\\n"
done
echo ${ACCOUNT_STRING}
rm -rf ~/.puppeth
rm -f genesis.json genesis-harmony.json
printf "2\n1\n2\n${BLOCK_INTERVAL}\n${ACCOUNT_STRING}yes\n${NETWORK_ID}\n2\n2\n\n" | puppeth --network genesis

gaslimit=$(printf '%x\n' ${BLOCK_SIZE})
jq -c ".gasLimit = \"0x${gaslimit}\"" genesis.json > tmp.$$.json && mv tmp.$$.json genesis.json

for index in ${!INSTANCE_LIST[@]}; do
    echo genesis init on ${INSTANCE_LIST[index]}
    gcloud compute scp genesis.json ${INSTANCE_LIST[index]}:~/genesis.json
    gcloud compute ssh ${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ init genesis.json"
    ACCOUNT=$(gcloud compute ssh ${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ account list | cut -d "{" -f2 | cut -d "}" -f1")
    #start the node
     gcloud compute ssh ${INSTANCE_LIST[index]} --command "geth --datadir .ethereum/ --syncmode 'full' --port 30311 --rpc --rpcaddr '0.0.0.0' --rpcport 8501 --rpcapi 'personal,db,eth,net,web3,txpool,miner' --bootnodes \"${BOOTNODE_ENODE}\" --networkid ${NETWORK_ID} --gasprice '1' -unlock ${ACCOUNT} --password password --allow-insecure-unlock --nousb --mine 2> exec.log"
done