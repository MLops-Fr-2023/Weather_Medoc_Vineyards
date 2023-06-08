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


######## Kubernetes  ########
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644


######## Other Librairies ########

### Cuda ###

#No GPU on the device : https://linuxhint.com/install-cuda-on-ubuntu-22-04-lts/

### PIP
export DEBIAN_FRONTEND=noninteractive
sudo apt install -y python3-pip
