#!/bin/bash

# git repo
export GIT_REPO="https://github.com/jcotoBan/marketplace-apps-test.git"
export WORK_DIR="/tmp/marketplace-apps-test/pythonScript" 

# install dependancies
export DEBIAN_FRONTEND=noninteractive
apt-get -qq update 2> /dev/null
apt-get -qq install -y git python3 python3-pip 2> /dev/null

# clone repo and set up ansible environment
git -C /tmp clone ${GIT_REPO} --quiet

# venv
cd ${WORK_DIR}
pip3 install virtualenv
python3 -m virtualenv env
source env/bin/activate
pip install pip --upgrade --quiet
pip install -r requirements.txt --quiet
clear
python3 main.py


if [ -d "/tmp/marketplace-apps-test/" ]; then
    rm -rf /tmp/marketplace-apps-test/
fi

