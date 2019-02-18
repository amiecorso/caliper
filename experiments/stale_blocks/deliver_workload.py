# Start small test network, deliver several IntKey transactions.
import docker
import time
import random

print("Delivering workload...")

NUM_VALIDATORS = 5
REST_URL_FORMATTER = "http://sawtooth-rest-api-default-{}:8008"

# Deliver IntKey workloads

docker_client = docker.from_env()
client = docker_client.containers.get("sawtooth-shell-default")

for i in range(100):
    which_val = random.randint(0, 4)
    intkey_command =  "intkey set --url " + REST_URL_FORMATTER.format(which_val) + " key" + str(i) + " " + str(i)
    client.exec_run(intkey_command)

docker_client.close()
