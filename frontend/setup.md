# setup
### Requirements
- docker
- docker-compose
### 1. Quickstart
This gets the django container up and running with a default administrator and password
- Install docker and docker-compose
- Build and start the containers
    ```
    docker-compose up
    ```
- Exit and shut down the containers with Ctrl + c
### 2. Configuration
#### docker-compose.yml
This file sets up a mysql and a django container and specifies the following information:
- Directories of the images' respective Dockerfiles
- Ports:  \<exposed port\>: \<docker port\>
    - note that changing the exposed mysql port will require a configuration change for the django container
- Volumes: directories for storing persistent data such as the mysql data directory and django source code
- Entrypoint: command runs upon entering the container
    - note: the django image's entrypoint script is located at onramp/server/
#### Set up initial user(s)
Initial users are created in a python script at onramp/server/createUsers.py. Modify this script as needed.
#### Set up mysql database credentials
- Mysql credentials are initially set up here: onramp/mysql/conf/mysqlSetup.sql. This script is only run on
    when building the container.
- Django database connection credentials must be adjusted to match the new login: onramp/server/ui/settings.py
#### Change mysql port
- Change the exposed port for the mysql image in docker-compose.yml
- Adjust the django settings file to connect to the new port: onramp/server/ui/settings.py
#### Change webserver port
- Change the exposed port for the django image in docker-compose.yml
### 3. Docker
Here are some useful commands for managing docker containers:
#### Docker
```
docker ps                     # list of running containers
docker image ls               # list installed docker images
docker volume ls              # list all volumes
docker container ls --all     # list all containers ran
docker stop <image_id>        # stops a docker container
docker rmi <image_id>         # delete a docker image
    -f                        # force
docker rm <container_id>      # delete a docker container
docker build <directory>      # build a docker image from a directory containing a Dockerfile
    -t <repository>:<tag>     # tag the image (shows up in docker image ls)
docker run <container_id>     # runs a docker image
    -p <port>:<dockerPort>    # forward requests to <port> to the docker container's exposed port
    -it                       # runs an interactive session
    -d --detach               # runs the docker in background and prints the id
    -rm                       # clean up filesystem after container exits
    --volume                  # add data volume to the image
    -e <NAME>=<VALUE>         # set environment variable inside container
docker stop <container_id>    # stops the specified container
docker system prune           # deletes all stopped containers, dangling images, and unused networks
docker network create <name>  # creates a network that docker images can share
```
#### Docker Compose
All these commands must be run in a directory with docker-compose.yml
```
docker-compose build          # builds all containers in the compose file
docker-compose up             # Builds, (re)creates, starts, and attaches to containers for a service
docker-compose run            # Runs a one-time command against a service
docker-compose stop           # Stops running containers without removing them. They can be started again with docker-compose start
docker-compose start          # Starts existing containers for a service.
docker-compose down           # Stops containers and removes containers, networks, volumes, and images created by up
docker-compose rm             # remove service containers
```
More useful commands can be found through online documentation
### 4. Troubleshooting
If docker-compose up tries to load old containers and crashes, run this to remove the old service containers
```
docker-compose rm                  
```