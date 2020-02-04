#!/usr/bin/env bash

CHECK=true
echo ""
echo "Welcome! Before you can run our tool, you need to make sure you have all the packages and libraries installed !"

echo ""
#checks if caliper is installed under /bin, if not it will be installed and also runs the caliper bind to conigure ethereum globally

echo ""
echo "We will procees further"
echo ""
if hash "jq" 2>/dev/null; then
  echo 'jq is installed'
else
  CHECK=false
  echo 'jq is missing.'
  echo 'Please follow this link: https://stedolan.github.io/jq/download/  to install jq'

fi

#Install and initialize the Cloud SDK using this link https://cloud.google.com/sdk/docs/?hl=de and install docker with this link https://docs.docker.com/install/linux/docker-ce/ubuntu/

if hash "gcloud" 2>/dev/null; then
  echo 'Google cloud SDK is installed. Please wait a few seconds..'
  echo 'Follow the link to log in please!'
  gcloud auth login
  echo " We will process.."

else
  CHECK=false
  echo 'Google cloud SDK is not installed. Please follow the instructions here: https://cloud.google.com/sdk/install'
fi

if hash "npm" 2>/dev/null; then
  echo 'npm is installed'
else
  CHECK=false
  echo 'npm is missing. Please download Node.js and follow the instructions in the link: https://www.npmjs.com/get-npm '
fi

if hash "geth" 2>/dev/null; then
  echo 'geth is installed'
else
  CHECK=false
  echo 'geth is missing. Please follow this link https://github.com/ethereum/go-ethereum/wiki/Installing-Geth to install geth'
fi

if hash "puppeth" 2>/dev/null; then
  echo 'puppeth is installed'
else
  CHECK=false
  echo 'puppeth is missing. Please follow this link https://www.sitepoint.com/puppeth-introduction/ to install puppeth'
fi
echo ""

cd bin/workload


if hash "caliper" 2>/dev/null; then
  echo 'Caliper is already installed'
else
  echo 'Caliper is not installed in /bin'
  echo 'We will process with installation'
  npm install
  echo 'We will run caliper bind to configure ethereum'
  npx caliper bind --caliper-bind-sut ethereum --caliper-bind-sdk 1.2.1
fi
cd -
echo ""

echo "Let's make sure that the needed python libraries are installed! "
echo ""

if python -c 'import pkgutil; exit(not pkgutil.find_loader("pandas"))'; then
  echo 'pandas is found'
else
  echo 'pandas is not found. We will install it now.'
  pip install pandas
  echo 'pandas is installed'
fi

if python -c 'import pkgutil; exit(not pkgutil.find_loader("lxml"))'; then
  echo 'lxml is found'
else
  echo 'lxml is not found. We will install it now.'
  pip install lxml
  echo 'lxml is installed'
fi

if python -c 'import pkgutil; exit(not pkgutil.find_loader("matplotlib"))'; then
  echo 'matplotlib is found'
else
  echo 'matplotlib is not found. We will install it now.'
  pip install matplotlib
  echo 'matplotlib is installed'
fi

if python -c 'import pkgutil; exit(not pkgutil.find_loader("numpy"))'; then
  echo 'numpy is found'
else
  echo 'numpy is not found. We will install it now.'
  pip install numpy
  echo 'numpy is installed'
fi
cd bin/sut

echo "Running script to create templates"
sh create-template.sh
echo "Templates created and Ethereum installed."
cd -

if $CHECK; then
  echo "Pre-requisites are all checked. Success"
else
  echo "Not all the Pre-requisites are installed."
fi
