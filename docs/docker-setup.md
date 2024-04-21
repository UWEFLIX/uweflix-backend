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
sudo docker run -d --restart=always -p 8888:443 IMAGE_ID
```

#### In this case python server inside docker is running in port 8888 and I want to run it in host's port 443

