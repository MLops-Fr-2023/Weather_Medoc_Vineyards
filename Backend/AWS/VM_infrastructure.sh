#!/bin/bash

##################################
############# Docker #############
##################################

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



##################################
##### Install Docker Engine ######
##################################

sudo apt-get update
sudo apt-get install -y ndocker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo apt  install docker-compose
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker



##################################
########## Kubernetes  ###########
##################################


curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644



##################################
######## Other Librairies ########
##################################


#### Cuda

#No GPU on the device : https://linuxhint.com/install-cuda-on-ubuntu-22-04-lts/

#### PIP
export DEBIAN_FRONTEND=noninteractive
sudo apt install -y python3-pip


#### GIT 

sudo apt update
sudo apt install git

# Source the .env file to set Git user.name and user.email
if [[ -f .env ]]; then
    source .env
    git config --global user.name "$GIT_USERNAME"
    git config --global user.email "$GIT_EMAIL"
else
    echo ".env file not found. Make sure to create the .env file with the required Git variables."
    exit 1
fi


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

# Source the .env file to set the AWS environment variables
if [[ -f .env ]]; then
    source .env
else
    echo ".env file not found. Make sure to create the .env file with the required AWS variables."
    exit 1
fi


#### ZSH 

# Check ZSH has been installed
if ! command -v zsh &>/dev/null; then
    echo "ZSH is not installed. Installing ZSH..."
    apt-get update
    apt-get install -y zsh
fi

# Change default shell for the current user
chsh -s "$(command -v zsh)" $(whoami)

# Install oh-my-zsh
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

# OPTIONAL

# Install zsh-syntax-highlighting plugin
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# Install zsh-autosuggestions plugin
git clone https://github.com/zsh-users/zsh-autosuggestions.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Add the plugins to ~/.zshrc
sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc