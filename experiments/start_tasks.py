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

compose_file = os.listdir(args.exp_dir + "/compose_files")[0].split("_")[-1]

start_network = "docker-compose -f {}compose_files/{}_{} up -d && sleep 10".format(args.exp_dir, str(args.n), compose_file)
subprocess.call(start_network, shell=True)

