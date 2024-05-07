# Docker Setup

#### Make sure docker is installed and running, follow official documentation to do so
#### Make a space to work in
```bash
mkdir uweflix-docker && cd uweflix-docker
```
```bash
git clone git@github.com:nishaalnaseer/uweflix-backend.git
```

## Setting up a Named Volume

#### Create Volume
```bash
sudo docker volume create uweflix
```

## Backend

#### We are going to running the backend server on the same network as host as this simplifies the process by a lot
#### Create the ```.env``` file and pull from git
#### Paste the Dockerfile 
#### Run to build the image
```bash
sudo docker build -t uweflix-backend .
```
#### To run it first get the image ID
```bash
sudo docker images
```

#### Finally run
```bash
sudo docker run -itd --restart=always --name uweflix-backend --network host --volume uweflix:/volume  uweflix-backend
```
#### In this case python server inside docker is running in port 443, and I'm going to host it on the same 'host' network, meaning its just another application as far as the host is concerned

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

## Run CertBot

```bash
sudo docker build -t certbot .
```

```bash
sudo docker run -itd --rm --name certbot --volume uweflix:/etc/letsencrypt certbot
```
```bash
sudo docker exec -it certbot /bin/bash 
```
```bash
certbot certonly --webroot
```

## Run NGINX
```bash
sudo docker build -t nginx .
```

```bash
sudo docker run -itd --restart=always --name nginx --network host \
-v ./nginx.conf:/etc/nginx/nginx.conf \
-v uweflix:/volume \
nginx
```

## Setting up the database
#### We are setting it up on the same host as docker is hosted (not on docker)
#### Edit ```/etc/mysql/mariadb.conf.d/50-server.cnf```, uncomment ```skip-name-resolve```
#### To grant rights to user root enter ```sudo mariadb``` and enter the following 
```
GRANT ALL PRIVILEGES ON *.* TO 'root'@'127.0.0.1' 
  IDENTIFIED BY '123' WITH GRANT OPTION;
```