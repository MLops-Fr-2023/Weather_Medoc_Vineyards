# Weather_Medoc_Vineyards
An application to help owners of vineyards in Margaux mitigate the effects of climate risks

### Launch the services

#### Optionnal full clean
From the folder *Backend* launch

`$ bash clean_docker.sh`

#### Launch
From the folder *Backend* launch

`$ bash run_docker_compose.sh`

### Execute the API tests : 
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

