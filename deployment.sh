#!/bin/bash

# git repo
export GIT_REPO="https://github.com/jcotoBan/marketplace-apps-test.git"
export WORK_DIR="/tmp/marketplace-apps-test" 

# install dependancies
apt-get update
apt-get install -y git python3 python3-pip

# clone repo and set up ansible environment
git -C /tmp clone ${GIT_REPO}

# venv
cd ${WORK_DIR}
pip3 install virtualenv
python3 -m virtualenv env
source env/bin/activate
pip install pip --upgrade
pip install -r requirements.txt
python3 ./pythonScript/main.py


