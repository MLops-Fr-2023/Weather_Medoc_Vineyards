#!/bin/bash

#################################
############## GIT ##############
#################################

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

#################################
############ AWS CLI ############
#################################


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


#################################
############# ZSH ###############
#################################

# Uninstall ZSH and Oh My Zsh
echo "Uninstalling ZSH and Oh My Zsh..."
sudo apt remove -y zsh
sudo rm -rf ~/.oh-my-zsh

# Check ZSH has been uninstalled
if command -v zsh &>/dev/null; then
    echo "ZSH uninstallation failed. Aborting..."
    exit 1
fi

# Check ZSH has been installed
if ! command -v zsh &>/dev/null; then
    echo "ZSH is not installed. Installing ZSH..."
    apt-get update
    apt-get install chsh -s "$(command -v zsh)" $(whoami) zsh
fi


# Install ZSH
echo "Installing ZSH..."
sudo apt update
sudo apt install -y zsh

# Change default shell for the current user
chsh -s "$(command -v zsh)" $(whoami)

# Install oh-my-zsh
echo "Installing Oh My Zsh..."
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" -y

# OPTIONAL

# Install zsh-syntax-highlighting plugin
echo "Installing zsh-syntax-highlighting plugin..."
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

# Install zsh-autosuggestions plugin
echo "Installing zsh-autosuggestions plugin..."
git clone https://github.com/zsh-users/zsh-autosuggestions.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

# Add the plugins to ~/.zshrc
echo "Adding plugins to ~/.zshrc..."
sed -i 's/plugins=(git)/plugins=(git zsh-autosuggestions zsh-syntax-highlighting)/' ~/.zshrc