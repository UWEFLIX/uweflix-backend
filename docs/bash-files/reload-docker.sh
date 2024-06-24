#!/bin/bash

sudo docker exec -it uweflix-backend /bin/bash -c "rm -rf *"
sudo docker cp uweflix-backend uweflix-backend:.
sudo docker restart uweflix-backend
