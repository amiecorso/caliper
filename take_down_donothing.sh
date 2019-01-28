docker-compose -f network/sawtooth/donothingnetwork/sawtooth-do-nothing.yaml down
docker rm $(docker ps -aq)
