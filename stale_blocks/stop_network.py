# Start small test network, deliver several IntKey transactions.
import subprocess

COMPOSE_FILE = "sawtooth-default.yaml"
REST_URL = "http://sawtooth-rest-api-default:8008"

COMPOSE_COMMAND = "docker-compose -f " + COMPOSE_FILE + " down"

# Stop network
subprocess.run(COMPOSE_COMMAND, shell=True)
