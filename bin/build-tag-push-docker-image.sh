#!/usr/bin/env bash
#TODO write a script that will push all our docker images to GC so we can use them
#Build an image from a Dockerfile-Xhorxhina

#$ git clone https://github.com/Cloud-Prototyping-WS-2019-20/cp_ws_1920.git

#ether-node
#build your image locally giving a tag for its repository
#$ docker  build /Users/[home]/cp_ws_1920/Docker/ether-node --tag ether-node
#$ gcloud auth configure-docker
#$ docker tag ether-node gcr.io/totemic-carrier-259013/ether-node 
#$ docker push gcr.io/totemic-carrier-259013/ether-node




#bootnode
#build your image locally giving a tag for its repository
#$ docker  build /Users/[home]/cp_ws_1920/Docker/bootnode --tag bootnode
#$ gcloud auth configure-docker
#$ docker tag bootnode gcr.io/totemic-carrier-259013/bootnode 
#$ docker push gcr.io/totemic-carrier-259013/bootnode



#sealer-node
#build your image locally giving a tag for its repository
#$ docker  build /Users/[home]/cp_ws_1920/Docker/seale-rnode --tag sealer-node
#$ gcloud auth configure-docker
#$ docker tag sealer-node gcr.io/totemic-carrier-259013/sealer-node
#$ docker push gcr.io/totemic-carrier-259013/sealer-node
