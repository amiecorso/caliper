# Start small test network, deliver several IntKey transactions.
import subprocess
import time

COMPOSE_FILE = "sawtooth-default.yaml"
REST_URL = "http://sawtooth-rest-api-default:8008"

COMPOSE_COMMAND = "docker-compose -f " + COMPOSE_FILE + " up"

# Start network
subprocess.run(COMPOSE_COMMAND, shell=True)
time.sleep(18) # wait for Docker containers to spin up


