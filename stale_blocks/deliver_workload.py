# Start small test network, deliver several IntKey transactions.
import docker
import time

REST_URL = "http://sawtooth-rest-api-default:8008"

# Deliver IntKey workloads

docker_client = docker.from_env()
client = docker_client.containers.get("sawtooth-shell-default")
print("CLIENT: ", client)

for i in range(10):
    intkey_command =  "intkey set --url " + REST_URL + " key" + str(i) + " " + str(i)
    client.exec_run(intkey_command)
    time.sleep(1)

docker_client.close()
