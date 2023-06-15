#!/bin/bash


########## Docker ##########
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

### Docker : Set up repository ###

#Update the apt package index and install packages to allow apt to use a repository over HTTPS:
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

#Add Docker’s official GPG key:
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

#Use the following command to set up the repository:
echo \
"deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
"$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null


### Install Docker Engine ###
sudo apt-get update
sudo apt-get install -y ndocker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt  install docker-compose
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker


######## Other Librairies ########

### Cuda ###

#No GPU on the device : https://linuxhint.com/install-cuda-on-ubuntu-22-04-lts/

### PIP
export DEBIAN_FRONTEND=noninteractive
sudo apt install -y python3-pip

### Install Pytorch
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

### Install fastai
pip install fastai

### Install TSai
pip install tsai

## Install classical librairies
pip install sklearn 
pip install matplotlib
pip install pandas
pip install numpy

### Install MLFlow
pip install mlflow[extras]
export PATH=/home/ubuntu/.local/bin:$PATH