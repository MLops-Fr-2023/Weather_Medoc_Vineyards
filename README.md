# Weather_Chateau_Margaux
An application to help owners of vineyards in Margaux mitigate the effects of climate risks

### Launch the services

#### Optionnal full clean
From the folder *Backend* launch

`$ bash run_docker_compose.sh`

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

