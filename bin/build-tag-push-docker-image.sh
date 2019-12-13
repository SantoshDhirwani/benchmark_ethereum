#!/usr/bin/env bash
#Build, tag and push images to google cloud registry
#Install and initialize the Cloud SDK using this link https://cloud.google.com/sdk/docs/?hl=de and install docker with this link https://docs.docker.com/install/linux/docker-ce/ubuntu/

set -e

#connect with your credentials to your google cloud account
gcloud auth configure-docker

#Build, tang and push images
#ether-node
cd ../Docker/ether-node
docker build --tag ether-node .
docker tag ether-node gcr.io/totemic-carrier-259013/ether-node
docker push gcr.io/totemic-carrier-259013/ether-node

#bootnode
#build your image locally giving a tag for its repository
cd ../bootnode
docker  build --tag bootnode .
docker tag bootnode gcr.io/totemic-carrier-259013/bootnode
docker push gcr.io/totemic-carrier-259013/bootnode

#sealer-node
#build your image locally giving a tag for its repository
cd ../sealer-node
docker  build --tag sealer-node .
docker tag sealer-node gcr.io/totemic-carrier-259013/sealer-node
docker push gcr.io/totemic-carrier-259013/sealer-node

#sealer-node
cd ../caliper
docker  build --tag caliper .
docker tag caliper gcr.io/totemic-carrier-259013/caliper
docker push gcr.io/totemic-carrier-259013/caliper

echo all images pushed succesfully!

