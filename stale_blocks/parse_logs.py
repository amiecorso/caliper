# Comb logs for all validators in network

import docker
import time

NUM_VALIDATORS = 5 # turn this into a command-line option?  Have it detected automatically?
REST_URL = "http://sawtooth-rest-api-default-0:8008"

docker_client = docker.from_env()

unique_blocks = set() # keep track of all valid blocks that have been seen by any validator

for i in range(NUM_VALIDATORS):
    val = docker_client.containers.get("sawtooth-validator-default-" + str(i)) 
    log = val.logs().decode('utf-8')
    splitlog = log.split("\n")
    for line in splitlog: 
        if "passed validation" in line:
            splitline = line.split() # split on spaces
            # find the block ID
            blockID = splitline[5]
            unique_blocks.add(blockID)

total_blocks = len(unique_blocks)

# now, find out which blocks have been committed to the official chain:
shell = docker_client.containers.get("sawtooth-shell-default")
output = shell.exec_run("sawtooth block list --url " + REST_URL)
print(output[1].decode('utf-8'))
output_lines = output[1].decode('utf-8').split("\n")

for line in output_lines:
    print(line)

num_blocks_longest_chain = len(output_lines) - 3 # <-- this 3 accounts for the header in the sawtooth block list command and the genesis block

stale_block_rate = (num_blocks_longest_chain - total_blocks) / total_blocks

print("Stale block rate: ", stale_block_rate)

# don't seem to need this but not sure why
#docker_client.close()
