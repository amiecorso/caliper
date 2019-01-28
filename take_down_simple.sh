docker-compose -f network/sawtooth/simplenetwork/sawtooth-simple.yaml down
docker rm $(docker ps -aq)
