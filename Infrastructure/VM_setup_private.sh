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

sudo apt-get update -y 
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt  install -y docker-compose --no-restart
sudo groupadd docker
sudo usermod -aG docker $USER


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

#### GIT

sudo apt update
sudo apt install -y git

# Source the .env_private file to set Git user.name and user.email
if [[ -f .env_private ]]; then
    source .env_private
    git config --global user.name "$GIT_USERNAME"
    git config --global user.email "$GIT_EMAIL"
else
    echo ".env_private file not found. Make sure to create the .env_private file with the required Git variables."
    exit 1
fi

# Configure Git to use SSH for authentication with GitHub
git config --global url."git@github.com:".insteadOf "https://github.com/"

#### AWS CLI

# Check architecture
architecture=$(uname -m)

if [[ $architecture == "aarch64" ]]; then
    echo "Detected ARM architecture. Installing AWS CLI for ARM..."
    sudo apt update
    sudo apt install -y unzip
    curl "https://awscli.amazonaws.com/awscli-exe-linux-aarch64.zip" -o "awscliv2.zip"
else
    echo "Detected x86 architecture. Installing AWS CLI for x86..."
    sudo apt update
    sudo apt install -y unzip
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
fi

# Extract and install AWS CLI
unzip awscliv2.zip
sudo ./aws/install

# Clean up
rm -rf awscliv2.zip

# Verify installation
aws --version

# Source the .env_private file to set the AWS environment variables
if [[ -f .env_private ]]; then
    source .env_private
else
    echo ".env_private file not found. Make sure to create the .env_private file with the required AWS variables."
    exit 1
fi

rm -f awscliv2.zip

logout

