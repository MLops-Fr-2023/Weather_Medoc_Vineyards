#!/bin/bash

export DEBIAN_FRONTEND=noninteractive



##################################
############# Docker #############
##################################

for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done

### Docker : Set up repository ###


# Update the apt package index and install packages to allow apt to use a repository over HTTPS:
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg

# Add Docker’s official GPG key:
sudo install -y -m 0755 -d /etc/apt/keyringsy
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Use the following command to set up the repository:
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null



##################################
##### Install Docker Engine ######
##################################

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo groupadd docker
sudo usermod -aG docker $USER



##################################
##### Install Docker Compose #####
##################################
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose



##################################
########## Kubernetes  ###########
##################################

curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644


##################################
######## Other Librairies ########
##################################

# CUDA: No GPU on the device - Skipping CUDA installation

#### PIP
sudo apt-get install -y python3-pip


# exec bash

