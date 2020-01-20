#!/bin/bash

set -e

############################################################
TEMPLATE_NAME=`cat ../config/config.json | awk '/template_name/{print $2}'`
INSTANCE_TEMPLATE_NAME=${TEMPLATE_NAME}
INSTANCE_NAME=${TEMPLATE_NAME}
ZONE=europe-west1-b
echo ${TEMPLATE_NAME}
############################################################

echo "Creating new instance"
gcloud compute instances create ${INSTANCE_NAME} \
    --image-family ubuntu-1804-lts --image-project gce-uefi-images \
    --metadata-from-file startup-script=./startup-script.sh \
    --zone=${ZONE}

echo SLEEPING FOR 30 SECONDS TO MAKE SURE INSTANCES ARE UP!
sleep 30

echo BOOTNODE CREATED!


echo "Creating VM template based on this launched instance"

gcloud compute instance-templates create ${INSTANCE_TEMPLATE_NAME} --source-instance ${INSTANCE_NAME} \
        --source-instance-zone ${ZONE}

#Stopping instance
echo "Stoping the instance after sucessfully creating a instance-template"
sleep 30
gcloud compute instances stop ${INSTANCE_NAME} --zone=${ZONE} -q
