# Start small test network, deliver several IntKey transactions.
import subprocess
import time

COMPOSE_FILE = "sawtooth-default.yaml"
#COMPOSE_FILE = "sawtooth-multi-poet.yaml"

COMPOSE_COMMAND = "docker-compose -f " + COMPOSE_FILE + " up"

# Start network
subprocess.run(COMPOSE_COMMAND, shell=True)

# not needed since sleeping from main.sh
# time.sleep(18) # wait for Docker containers to spin up


