# Docker Setup

## Backend
#### Make sure docker is installed and running, follow official documentation to do so
#### Make a space to work in
```bash
mkdir uweflix-docker
```

#### Create the ```.env``` file and pull from git
#### Paste the Dockerfile 
#### Run to build the image
```bash
sudo docker build -t controller .
```
#### To run it first get the image ID
```bash
sudo docker images
```

#### Finally run
```bash
sudo docker run -itd --restart=always --name uweflix-backend --network host uweflix-backend
```
#### In this case python server inside docker is running in port 8888 and I want to run it in host's port 443

#### To get the container ID
```bash
sudo docker ps
```

#### Stop container
```bash
sudo docker stop uweflix-backend
```

#### View log 
```bash
sudo docker logs uweflix-backend
```

#### Follow logs 
```bash
sudo docker logs -f uweflix-backend
```


## Setting up the database
#### We are setting it up on the same host as docker is hosted
#### Edit ```/etc/mysql/mariadb.conf.d/50-server.cnf```, uncomment ```skip-name-resolve```