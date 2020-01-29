#!/usr/bin/env bash
#Deploy SUT script
# ./deploy-sut.sh <number of nodes> <block interval> <block size>

set -e

NUMBER_NODES=${1}
BLOCK_INTERVAL=${2}
BLOCK_SIZE=${3}
INSTANCE_GROUP_NAME=ethereum-sut-group
BOOT_NODE_NAME=bootnode
INSTANCE_TEMPLATE=ethereum-sut-template

#receiving the values of GCP Setup, Username, Password and NetworkID from config.json
NEW_SETUP=$(jq -r '.GCP_SETUP'  ../config/config.json) # 1: clean, 0: don't clean previous setup
USERNAME=$(jq -r '.USERNAME'  ../config/config.json)
PASSWORD=$(jq -r '.PASSWORD'  ../config/config.json)
NETWORK_ID=$(jq -r '.NETWORK_ID'  ../config/config.json)

# clean previous sut

if [ X${NEW_SETUP} == "X1" ]
then
echo DELETING PREVIOUS SETUP, THIS MIGHT TAKE SOME TIME...
echo
echo | gcloud -q compute instance-groups managed delete ${INSTANCE_GROUP_NAME} || true
echo | gcloud -q compute instances delete ${BOOT_NODE_NAME} || true
echo
echo PREVIOUS SETUP DELETED

# run bootnode
echo ---- CREATING BOOTNODE ----
gcloud compute instances create ${BOOT_NODE_NAME} --source-instance-template ${INSTANCE_TEMPLATE}
echo BOOTNODE CREATED!
echo SLEEPING FOR 30 SECONDS TO MAKE SURE BOOTNODE IS UP...
sleep 30

# create instance group of sealer nodes
echo
echo ---- CREATING NODES ----
gcloud compute instance-groups managed create ${INSTANCE_GROUP_NAME} \
   --base-instance-name ethereum-sut \
   --size ${NUMBER_NODES} \
   --template ${INSTANCE_TEMPLATE}

gcloud compute instance-groups managed set-autoscaling ${INSTANCE_GROUP_NAME} \
  --max-num-replicas=${NUMBER_NODES} \
  --min-num-replicas=${NUMBER_NODES}

echo SLEEPING FOR 30 SECONDS TO MAKE SURE INSTANCES ARE UP!
sleep 30
fi

IP_BOOTNODE=$(gcloud compute instances list --filter="name~${BOOT_NODE_NAME}" --format='value(INTERNAL_IP)')
gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "killall bootnode || true"
gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "rm -f boot.key && bootnode -genkey boot.key"
gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "nohup bootnode -nodekey boot.key -addr 0.0.0.0:30310 > /dev/null 2>&1 &"
BOOTNODE_PID=$(gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "pgrep bootnode || true")
if [ X${BOOTNODE_PID} == "X" ]
then
    echo bootnode process is not running
   exit 0
else
    echo bootnode running with process id ${BOOTNODE_PID}
fi

key=$(gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "cat boot.key")
hex=$(gcloud compute ssh ${USERNAME}@${BOOT_NODE_NAME} --command "bootnode -nodekeyhex $key -writeaddress")
BOOTNODE_ENODE=enode://${hex}@${IP_BOOTNODE}:30310?discport=30310

echo THE BOOTNODE ENODE ADDRESS IS: ${BOOTNODE_ENODE}

prefix=$(gcloud compute instance-groups managed list --format='value(baseInstanceName)' --filter='name~^'${INSTANCE_GROUP_NAME}'')
INSTANCE_LIST=( $(gcloud compute instances list --sort-by ~NAME --filter="name~^${prefix}" --format='value(name)') )
ACCOUNT_LIST=()

# create accounts on nodes
echo ---- CREATING ACCOUNTS ON NODES ----
for index in ${!INSTANCE_LIST[@]}; do
    echo CREATING GETH ACCOUNT ON ${INSTANCE_LIST[index]}
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "rm -rf .ethereum"
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "killall geth || true"
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "echo ${PASSWORD} > password && geth --datadir .ethereum/ account new --password password"
    ACCOUNT=$(gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ account list | cut -d "{" -f2 | cut -d "}" -f1")
    ACCOUNT_LIST[index]=${ACCOUNT}
done

ACCOUNT_STRING=""
INSTANCE_IP_LIST=( $(gcloud compute instances list --sort-by ~NAME --filter="name~^${prefix}" --format='value(EXTERNAL_IP)') )
INSTANCES_STRING=""

for index in ${!ACCOUNT_LIST[@]}; do
    INSTANCES_STRING+="${INSTANCE_IP_LIST[index]}:8501:${ACCOUNT_LIST[index]}:${PASSWORD}\\n"
    ACCOUNT_STRING+="${ACCOUNT_LIST[index]}\\n"
done
echo ${INSTANCES_STRING} > run_caliper.conf
ACCOUNT_STRING+="\\n"

echo ---- ACCOUNTS CREATED ----
echo ${ACCOUNT_STRING}
echo ---- PREPARING GENESIS FILE ----
rm -rf ~/.puppeth
rm -f genesis.json genesis-harmony.json
printf "2\n1\n2\n${BLOCK_INTERVAL}\n${ACCOUNT_STRING}${ACCOUNT_STRING}yes\n${NETWORK_ID}\n2\n2\n\n" | puppeth --network genesis || true

gaslimit=$(printf '%x\n' ${BLOCK_SIZE})
jq -c ".gasLimit = \"0x${gaslimit}\"" genesis.json > tmp.$$.json && mv tmp.$$.json genesis.json
echo ---- CONFIGURING AND RUNNING GETH IN NODES ----
for index in ${!INSTANCE_LIST[@]}; do
    echo GENESIS INIT ON ${INSTANCE_LIST[index]}
    gcloud compute scp genesis.json ${USERNAME}@${INSTANCE_LIST[index]}:~/genesis.json
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ init genesis.json"
    echo
    echo GENESIS INITIALISED on ${INSTANCE_LIST[index]}
    ACCOUNT=$(gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "geth --nousb --datadir .ethereum/ account list | cut -d "{" -f2 | cut -d "}" -f1")
    #start the node
    gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "nohup geth --datadir .ethereum/ --syncmode 'full' --port 30311 --rpc --rpcaddr '0.0.0.0' --rpcport 8501 --rpcapi 'personal,db,eth,net,web3,txpool,miner' --bootnodes \"${BOOTNODE_ENODE}\" --networkid ${NETWORK_ID} --gasprice '1' --unlock 0x${ACCOUNT} --password password --allow-insecure-unlock --nousb --mine --rpccorsdomain '*' --nat 'any' > /dev/null 2>&1 &"
    GETH=$( gcloud compute ssh ${USERNAME}@${INSTANCE_LIST[index]} --command "pgrep geth")
    if [ X${GETH} == "X" ]
    then
        echo geth process is not running on nodes
        exit 0
    else
        echo geth running on ${INSTANCE_LIST[index]} with process id ${GETH}
    fi
done
exit 0
