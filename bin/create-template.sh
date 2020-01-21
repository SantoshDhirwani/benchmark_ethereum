#!/bin/bash

set -e

###########ENVIRONMENT_VARIBALES############################
VM_TEMPLATE_NAME=$(cat ../config/config.json | awk  '/templateName/{print $2}' | sed 's/\"//g' )
RANDOM_ID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 8 | head -n 1)
INSTANCE_NAME=${VM_TEMPLATE_NAME}
ZONE=europe-west1-b
IMAGE_FAMILY=ubuntu-1804-lts
IMAGE_PROJECT=ubuntu-os-cloud
SCRIPT_PATH=./startup-script.sh
############################################################
echo "VM Template Name" $VM_TEMPLATE_NAME

echo "Creating new instance"

echo "VM Instance Name" $INSTANCE_NAME

gcloud compute instances create $INSTANCE_NAME \
	--image-family $IMAGE_FAMILY --image-project $IMAGE_PROJECT \
	--metadata-from-file startup-script=$SCRIPT_PATH \
	--zone=$ZONE

echo SLEEPING FOR 30 SECONDS TO MAKE SURE INSTANCES ARE UP!
sleep 30

echo "Allowing HTTP"
gcloud compute firewall-rules create ${INSTANCE_NAME} --allow tcp

echo "Instance setup finished. ${INSTANCE_NAME} is ready to use."

echo "Creating VM template based on this launched instance"

gcloud compute instance-templates create $VM_TEMPLATE_NAME --source-instance $INSTANCE_NAME \
	--source-instance-zone $ZONE

echo "Stopping the instance after sucessfully creating a VM-template"
gcloud compute instances stop $INSTANCE_NAME --zone=$ZONE -q
sleep 1

echo "Template Created and VM $INSTANCE_NAME Stopped Successfully"
