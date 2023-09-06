# Weather Medoc Vineyards
The application to assist vineyard owners in Médoc (France) with mitigating the effects of climate risks

## Quick start (standalone installation)
- Install and launch Docker-Desktop
- Clone the repository
- From the root of the repository run the following command line :
`./run_solution_standalone.sh`

You will perhaps need to give permissions to execute the scripts with the following command line:

`chmod +x run_solution_standalone.sh stop_and_clean_solution.sh`

The services are reachable with the following url : 
- **API** : http://localhost:8000/docs
- **Airflow** : http://localhost:8080/
- **Mlflow** : http://localhost:5001/
- **Flower** : http://localhost:9001/
- **Streamlit** : http://localhost:8501/

## Advanced start
#### Launch Backend part
From the folder *Backend* launch

`$ bash run_docker_compose.sh`

#### Optionnal full clean
From the folder *Backend* launch

`$ bash clean_docker.sh`

#### Execute the API tests : 
Once the services started, from the folder *Backend* launch

`$ docker-compose -f docker-compose.test.yml  up --build`

### Access :

#### If all services on the same VM
All the ressources would be accesssible through their exposed ports (5555, 8080, 5001) and with Nginx Proxy on 9001, 9002, 9003

#### If service in differents VM, separated on differents subnets (private/public)
For le final architecture, service would be accessible from outside the VPC through the Nginx Proxy on 9001, 9002, 9003

### Quick manual setup on a new AWS VM (t3.large)
```
# AWS VL from scratch
sudo apt-get update && sudo apt-get upgrade 
sudo apt install docker-compose

# prepare for docker 
sudo usermod -aG docker $USER
# sudo groupadd docker
newgrp docker

# generate RSA key
ssh-keygen -t rsa -b 4096 -C "myaccountemail@gmail.com"
cat /home/ubuntu/.ssh/id_rsa.pub
# create key in personal github account

# clone repo
git clone git@github.com:MLops-Fr-2023/Weather_Medoc_Vineyards.git
cd Weather_Medoc_Vineyards/
git checkout develop

# run services
cd Backend
./run_docker_compose.sh
```

# Infrastructure part.

## Presentation

In this project you will find an AWS folder in order to run your application according to the IaaS (Infrastructure as a Service)
The folder contains :
- The infrastructure.yml file which must be used with CloudFormation
- The VM_setup.sh to set up a VM (Docker, Kubernetes, Git, AWS CLI)
- bucket_folders.sh which must be use from a VM INSIDE the private subnet and before to deploy the application. This files allows the creation of subfolders inside the bucket
- The folder bucket_documents

NB : Folder and subfolders will be created, but they are empty. Please fill them according to the folder present on this repo : bucket_documents
NB_bis : Verify that the name you give to your bucket in the IaS is the same as the name of the bucket in the bucket_folders.sh

## Protocol


###Create the PRIVATE AMI:
- Fill the Infrastructure/.env_private file with your personnal information
- Create a VM according to your requirements. Do not forget to allow IP association otherwise you'll not be able to connect. Provide at least 50g of EBS.
- Once the VM started, connect to your VM
- Clone the repo : https://github.com/MLops-Fr-2023/Weather_Medoc_Vineyards.git
- Execute the following command :
```
    cd Weather_Medoc_Vineyards/Infrastructure
    sudo bash VM_setup_private.sh
    'Y' or 'Yes' if requiered
    cd ~
    sudo rm -rf Weather_Medoc_Vineyards
```
- Create an SSHkey to allow Github communication
```
    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    cat ~/.ssh/id_rsa.pub
```
    
    - Copy the printed Key and paste it in the SSH key section of your Github Account - Name it "Prod_VM_Private_AMI"
- From your AWS consol, create a AMI instance from your newly setted up VM
- Kill the VM
- Copy/Paste the ID of the AMI in the AmiIdentifierPrivate.Default section of infrastructure.yml


###Create the PUBLIC AMI:
- Fill the Infrastructure/.env_public file with your personnal information
- Create a VM according to your requirements. Do not forget to allow IP association otherwise you'll not be able to connect. Provide 30g of EBS.
- Once the VM started, connect to your VM
- Clone the repo : https://github.com/MLops-Fr-2023/Weather_Medoc_Vineyards.git
- Execute the following command :
```
    cd Weather_Medoc_Vineyards/Infrastructure
    sudo bash VM_setup_public.sh
    'Y' or 'Yes' if requiered
    cd ~
    sudo rm -rf Weather_Medoc_Vineyards
```
- Create an SSHkey to allow Github communication
```
    ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
    cat ~/.ssh/id_rsa.pub
```

    - Copy the printed Key and paste it in the SSH key section of your Github Account - Name it "Prod_VM_Public_AMI"
- From your AWS consol, create a AMI instance from your newly setted up VM
- Kill the VM
- Copy/Paste the ID of the AMI in the AmiIdentifierPublic.Default section of infrastructure.yml


###Create the Infrastructure
- Launch the IaS Stack from CloudFormation
- Set up a bastion Host to access your VMs on the private subnet (https://dev.to/aws-builders/ssh-setup-and-tunneling-via-bastion-host-3kcc or any other technics)
- Clone the repo : git@github.com:MLops-Fr-2023/Weather_Medoc_Vineyards.git
- Modify 'bucket_folders.sh' according to the name of your bucket and launch with
    - sudo bash bucket_folders.sh
