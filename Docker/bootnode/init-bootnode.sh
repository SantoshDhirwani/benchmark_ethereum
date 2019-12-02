#!/bin/sh

# get the private ip of the host
PRIVATE_HOST_IP=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)

# uncomment if you want to generate boot key
#bootnode -genkey boot.key

# start boot node to bootstrap the network
bootnode -nodekey boot.key -verbosity 9 -addr ${PRIVATE_HOST_IP}:3031
