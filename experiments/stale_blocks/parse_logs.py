#Comb logs for all validators in network
# TODO: figure out how/why different logs use different terminology to deal with block validation
#       make this more robust than a simple IF/ELSE.... based on versions?/consensus?
# Better yet, use event subscription to make this universal

import docker
import time
import argparse

parser = argparse.ArgumentParser(description="Parse validator logs for stale block rate")
parser.add_argument('--n', default=1, type=int, help="Network size")
parser.add_argument('--dest', default='/home/amie/caliper/experiments/prototest/results/', help="Where parsing results should be stored")
parser.add_argument('--rest_url', default='http://sawtooth-rest-api-default:8008', help="URL of a rest-api container for this network") # defaults to size 1 network
parser.add_argument('--val_name', default ='sawtooth-validator-default', help="base name for validator containers") # default to size 1 network
parser.add_argument('--shell_name', default='sawtooth-shell-default', help="name of shell container")
parser.add_argument('--single', default=False, action='store_const', const=True,  help="Include this flag if val_name should be left un-appended")
args = parser.parse_args()

output_file = args.dest + str(args.n) + "_stale.csv"

docker_client = docker.from_env()

unique_blocks = set() # keep track of all valid blocks that have been seen by any validator

for i in range(args.n):
    if args.single:
        val_container = args.val_name
    else:
        val_container = args.val_name + "-" + str(i)
    val = docker_client.containers.get(val_container) 
    log = val.logs().decode('utf-8')
    print("LOG: ", log)
    splitlog = log.split("\n")
    for line in splitlog: 
        if "passed validation" in line:
            splitline = line.split() # split on spaces
            # find the block ID
            blockID = splitline[5]
            unique_blocks.add(blockID)
        elif "Finished block validation of" in line:
            splitline = line.split() # split on spaces
            blockID = splitline[8]
            unique_blocks.add(blockID)

total_blocks = len(unique_blocks)

# now, find out which blocks have been committed to the official chain:
shell = docker_client.containers.get(args.shell_name)
output = shell.exec_run("sawtooth block list --url " + args.rest_url)
print("Block list main chain: ", output[1].decode('utf-8'))
output_lines = output[1].decode('utf-8').split("\n")
'''
for line in output_lines:
    print(line)
'''
num_blocks_longest_chain = len(output_lines) - 3 # <-- this 3 accounts for the header in the sawtooth block list command and the genesis block

if not total_blocks:
    print("Error: failed to find any blocks while parsing validator logs")
    stale_block_rate = "error - found no blocks while parsing logs"
else:
    stale_block_rate = (total_blocks - num_blocks_longest_chain) / total_blocks

print("Unique valid blocks: ", unique_blocks)
print("Stale block rate: ", stale_block_rate)
with open(output_file, 'w') as f:
    f.write(str(stale_block_rate))

# don't seem to need this but not sure why
#docker_client.close()
