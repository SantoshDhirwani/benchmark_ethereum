#!/usr/bin/env bash
#TODO write a script that will push all our docker images to GC so we can use them
#Before you start be sure, THAT billing is enabled for your Google Cloud project and Enable the Container Registry API.
#Install and initialize the Cloud SDK using this link https://cloud.google.com/sdk/docs/?hl=de and install docker with this link https://docs.docker.com/install/linux/docker-ce/ubuntu/

#Build an image from a Dockerfile-Xhorxhina
#ether-node
#build your image, and check it with command " docker images " to verify that the image was build
 cd ../Docker/ether-node
 docker build ether-node  --tag ether-node

#connect with you credentials to your google cloud account, and make sure the billing is enabled
 gcloud auth configure-docker
 docker tag ether-node gcr.io/totemic-carrier-259013/ether-node 
 docker push gcr.io/totemic-carrier-259013/ether-node

#bootnode
#build your image locally giving a tag for its repository
 cd ../Docker/bootnode
 docker  build bootnode --tag bootnode
 docker tag bootnode gcr.io/totemic-carrier-259013/bootnode 
 docker push gcr.io/totemic-carrier-259013/bootnode

#sealer-node
#build your image locally giving a tag for its repository
 cd ../Docker/sealer-node
 docker  build sealer-node --tag sealer-node
 docker tag sealer-node gcr.io/totemic-carrier-259013/sealer-node
 docker push gcr.io/totemic-carrier-259013/sealer-node

  cd ../Docker/sealer-node
 docker  build sealer-node --tag caliper
 docker tag sealer-node gcr.io/totemic-carrier-259013/caliper
 docker push gcr.io/totemic-carrier-259013/caliper

