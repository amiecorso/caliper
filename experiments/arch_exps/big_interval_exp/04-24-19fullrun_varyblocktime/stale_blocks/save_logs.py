# save_logs.py
# Save logs for all containers in network - diagnostic

import docker
import time
import argparse
import os

parser = argparse.ArgumentParser(description="Save Docker container logs for scrutiny")
parser.add_argument('--n', default=1, type=int, help="Network size")
parser.add_argument('--exp_dir', help="Which experiment are we parsing?")
parser.add_argument('--run_num', help="Which run of the experiment is this?")
parser.add_argument('--tps')
parser.add_argument('--interval')
args = parser.parse_args()

# make the output directory if it doesn't exist yet
if not args.exp_dir.endswith("/"):
    args.exp_dir += "/"
LOGS_DIR = args.exp_dir + "LOGS/"
if not os.path.exists(LOGS_DIR):
    os.mkdir(LOGS_DIR)
OUTPUT_DIR = LOGS_DIR + str(args.n) + "/"
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)
TPS_DIR = OUTPUT_DIR + args.tps + "tps/"
if not os.path.exists(TPS_DIR):
    os.mkdir(TPS_DIR)
INTERVAL_DIR = TPS_DIR + args.interval + "sec/"
if not os.path.exists(INTERVAL_DIR):
    os.mkdir(INTERVAL_DIR)
RUN_DIR = INTERVAL_DIR + "run" + args.run_num + "/"
if not os.path.exists(RUN_DIR):
    os.mkdir(RUN_DIR)

compose_file = None
for f in os.listdir(args.exp_dir + "compose_files"):
    if (f.startswith(str(args.n))):
        compose_file = f
        break
if not compose_file: # if we can't find file
    raise Exception("There is no compose file for network size {}".format(str(args.n)))

docker_client = docker.from_env()

with open(args.exp_dir + "compose_files/" + compose_file, 'r') as f:
    lines = f.readlines()

for line in lines:
    if "container_name" in line:
        container_name = line.split(":")[-1].strip() # grab the container name from the .yaml file
        container = docker_client.containers.get(container_name)
        log = container.logs().decode('utf-8')
        with open(RUN_DIR + "/" + container_name, 'w') as out:
            out.write(log)

