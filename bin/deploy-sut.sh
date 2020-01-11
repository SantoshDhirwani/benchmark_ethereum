#!/usr/bin/env bash
#Deploy SUT script
# ./deploy-sut.sh <number of nodes> <block interval> <block size>

NUMBER_NODES=${1}
BLOCK_INTERVAL=${2}
BLOCK_SIZE=${3}
INSTANCE_GROUP_NAME=ethereum-sut-group
BOOT_NODE_NAME=bootnode
INSTANCE_TEMPLATE=ethereum-sut-template
USERNAME=cloudproto

NETWORK_ID=123

# clean previous sut
echo DELETING PREVIOUS SETUP, THIS MIGHT TAKE SOME TIME...
echo
echo | gcloud -q compute instance-groups managed delete ${INSTANCE_GROUP_NAME}
echo | gcloud -q compute instances delete ${BOOT_NODE_NAME}
echo PREVIOUS SETUP DELETED
# run bootnode
echo ---- CREATING BOOTNODE ----
gcloud compute instances create ${BOOT_NODE_NAME} --source-instance-template ${INSTANCE_TEMPLATE}
echo SLEEPING FOR 60 SECONDS TO MAKE SURE BOOTNODE IS UP!
sleep 60

IP_BOOTNODE=$(gcloud compute instances list --filter="name~${BOOT_NODE_NAME}" --format='value(INTERNAL_IP)')
gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "nohup bootnode -genkey boot.key"
gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "bootnode -nodekey boot.key -addr 0.0.0.0:30310 >> exec.log &"
key=$(gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "cat boot.key")
hex=$(gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "nohup bootnode -nodekeyhex $key -writeaddress")
BOOTNODE_ENODE=enode://${hex}@${IP_BOOTNODE}:30310?discport=30310

echo THE BOOTNODE ENODE ADDRESS IS: ${BOOTNODE_ENODE}

# create instance group of sealer nodes
echo ---- CREATING NODES ----
gcloud compute instance-groups managed create ${INSTANCE_GROUP_NAME} \
   --base-instance-name ethereum-sut \
   --size ${NUMBER_NODES} \
   --template ${INSTANCE_TEMPLATE}

echo SLEEPING FOR 60 SECONDS TO MAKE SURE INSTANCES ARE UP!
sleep 60

prefix=$(gcloud compute instance-groups managed list --format='value(baseInstanceName)' --filter='name~^'${INSTANCE_GROUP_NAME}'')
INSTANCE_LIST=( $(gcloud compute instances list --filter="name~^${prefix}" --format='value(name)') )
ACCOUNT_LIST=()

# create accounts on nodes
echo ---- CREATING ACCOUNTS ON NODES ----
for index in ${!INSTANCE_LIST[@]}; do
    echo CREATING GETH ACCOUNT ON ${INSTANCE_LIST[index]}
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "echo password >> password && geth --datadir .ethereum/ account new --password password"
    ACCOUNT=$(gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ account list | cut -d "{" -f2 | cut -d "}" -f1")
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
echo ---- CONFIGURING AND RUNNING GETH IN NODES ----
for index in ${!INSTANCE_LIST[@]}; do
    echo GENESIS INIT ON ${INSTANCE_LIST[index]}
    gcloud compute scp genesis.json ${USERNAME}@${INSTANCE_LIST[index]}:~/genesis.json
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ init genesis.json"
    ACCOUNT=$(gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ account list | cut -d "{" -f2 | cut -d "}" -f1")
    #start the node
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --datadir .ethereum/ --syncmode 'full' --port 30311 --rpc --rpcaddr '0.0.0.0' --rpcport 8501 --rpcapi 'personal,db,eth,net,web3,txpool,miner' --bootnodes \"${BOOTNODE_ENODE}\" --networkid ${NETWORK_ID} --gasprice '1' -unlock ${ACCOUNT} --password password --allow-insecure-unlock --nousb --mine 2> exec.log &"
done
exit 0