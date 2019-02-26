# start_tasks.py

import subprocess
import os
import argparse

print("Executing start_tasks.py")
parser = argparse.ArgumentParser(description="Execute pre-workload tasks for Caliper experiment")
parser.add_argument("--n", default=1, type=int, help="Number of validators in network")
parser.add_argument("--exp_dir", default="~/caliper/experiments/poet_prototest", help="The directory for this experiment")
args = parser.parse_args()

if not args.exp_dir.endswith("/"):
    args.exp_dir = args.exp_dir + "/"

compose_file = [f for f in os.listdir(args.exp_dir + "/compose_files") if f.startswith(str(args.n))][0]

start_network = "docker-compose -f {}compose_files/{} up -d && sleep 10".format(args.exp_dir, compose_file)
print("Starting network... ")
print("Executing command: ", start_network)
subprocess.call(start_network, shell=True)

