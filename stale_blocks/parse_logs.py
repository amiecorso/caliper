# Start small test network, deliver several IntKey transactions.
import docker
import time

NUM_VALIDATORS = 1
REST_URL = "http://sawtooth-rest-api-default:8008"

# Deliver IntKey workloads

docker_client = docker.from_env()

for i in range(NUM_VALIDATORS):
    val = docker_client.containers.get("sawtooth-validator-default")
    log = val.logs().decode('utf-8')
    # TODO: parse log!  it's a giant string at this point.

docker_client.close()
