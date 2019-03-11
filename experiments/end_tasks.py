# end_tasks.py

import subprocess
import os
import argparse

print("Executing end_tasks.py")
parser = argparse.ArgumentParser(description="Execute post-workload tasks for Caliper experiment")
parser.add_argument("--n", default=1, type=int, help="Number of validators in network")
parser.add_argument("--exp_dir", default="~/caliper/experiments/poet_prototest", help="The directory for this experiment")
args = parser.parse_args()

if not args.exp_dir.endswith("/"):
    args.exp_dir = args.exp_dir + "/"

compose_file = [f for f in os.listdir(args.exp_dir + "compose_files") if f.startswith(str(args.n))][0] 

# read and detect name of validator container and rest-api-url for passing to parse_logs.py:
with open(args.exp_dir + "compose_files/" + compose_file, 'r') as f:
    conts = f.readlines()
    for line in conts:
        if ("container_name") in line and ("validator" in line):
            val_name = ("-").join(line.split(":")[-1].strip().split("-")[:-1])
            break
    for line in conts:
        if ("container_name" in line) and ("rest-api" in line):
            rest_name = line.split(":")[-1].strip()
            rest_url = "http://" + rest_name + ":8008"
            break

print("end_tasks.py: Calling save_logs.py")
save_logs = "python3 ~/caliper/experiments/stale_blocks/save_logs.py --n {} --exp_dir {} && sleep 4".format(str(args.n), args.exp_dir)
subprocess.call(save_logs, shell=True)

print("end_tasks.py: Calling parse_logs.py...")
print("     val container name: ", val_name)
print("     rest url: ", rest_url)
parse_logs = "python3 ~/caliper/experiments/stale_blocks/parse_logs.py --n {} --dest {}results/ --val_name {} --rest_url {} && sleep 10".format(str(args.n), args.exp_dir, val_name, rest_url)
subprocess.call(parse_logs, shell=True)

print("end_tasks.py: Taking down network")
take_down = "docker-compose -f {}compose_files/{} down".format(args.exp_dir, compose_file)
subprocess.call(take_down, shell=True)

subprocess.call("docker volume prune -f", shell=True)

print("end_tasks.py: Calling report_parser.py")
parse_reports = "python3 ~/caliper/experiments/data_scripts/report_parser.py --reportpath {} --dest {}results/ --n {}".format(args.exp_dir, args.exp_dir, str(args.n))
subprocess.call(parse_reports, shell=True)
