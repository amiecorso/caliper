# end_tasks.py

import subprocess
import os
import argparse
import time

print("Executing end_tasks.py")
parser = argparse.ArgumentParser(description="Execute post-workload tasks for Caliper experiment")
parser.add_argument("--n", default=1, type=int, help="Number of validators in network")
parser.add_argument("--exp_dir", default="~/caliper/experiments/poet_prototest", help="The directory for this experiment")
parser.add_argument("--run_num", help="Which run is this? For multiple rounds of identical experiments")
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

#This seems to help the sawtooth block list command display the correct blocks/txns
time.sleep(20)

print("end_tasks.py: Calling save_logs.py")
save_logs = "python3 ~/caliper/experiments/stale_blocks/save_logs.py --n {} --exp_dir {} --run_num {} && sleep 4".format(str(args.n), args.exp_dir, args.run_num)
subprocess.call(save_logs, shell=True)

# NEED TO RETHINK STALE BLOCK CALCULATIONS
# currently, this would calculate stale blocks for the WHOLE experimental run (including all sub-rounds...)
# need to EITHER:
#   - change the way workloads are delivered so that it is one rate per benchmark (thus a meaningful SBR calculation)
#   - change the log parsing to grab from a specific window of time (this would be very complicated because sawtooth block list lists ALL blocks not just from a specific window, though it seems we could ask for blocks published in the same window from which the logs are being probed...)
#   - run separate experiments to determine SBR once throughput window has been established for network size?
# would the stale block rate be meaningful if tested at a rate that was strictly higher than maximum determinable throughput... I think it would?

'''
print("end_tasks.py: Calling parse_logs.py...")
print("     val container name: ", val_name)
print("     rest url: ", rest_url)
parse_logs = "python3 ~/caliper/experiments/stale_blocks/parse_logs.py --n {} --dest {}results/ --val_name {} --rest_url {} && sleep 10".format(str(args.n), args.exp_dir, val_name, rest_url)
subprocess.call(parse_logs, shell=True)
'''


print("end_tasks.py: Taking down network")
take_down = "docker-compose -f {}compose_files/{} down".format(args.exp_dir, compose_file)
subprocess.call(take_down, shell=True)

subprocess.call("docker volume prune -f", shell=True)

print("end_tasks.py: Calling report_parser.py")
parse_reports = "python3 ~/caliper/experiments/data_scripts/report_parser.py --reportpath {} --results {}results/ --n {} --run_num {}".format(args.exp_dir, args.exp_dir, str(args.n), str(args.run_num))
subprocess.call(parse_reports, shell=True)
