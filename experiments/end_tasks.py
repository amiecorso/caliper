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

compose_file = os.listdir(args.exp_dir + "/compose_files")[0].split("_")[-1]

parse_logs = "python3 ~/caliper/experiments/stale_blocks/parse_logs.py --n {} --dest {}results/ --rest_url http://sawtooth-rest-api-default-0:8008 && sleep 10".format(str(args.n), args.exp_dir)
subprocess.call(parse_logs, shell=True)

take_down = "docker-compose -f {}compose_files/{}_{} down".format(args.exp_dir, str(args.n), compose_file)
subprocess.call(take_down, shell=True)

subprocess.call("docker volume prune -f", shell=True)

parse_reports = "python3 ~/caliper/experiments/data_scripts/report_parser.py --reportpath {} --dest {}results/ --n {}".format(args.exp_dir, args.exp_dir, str(args.n))
subprocess.call(parse_reports, shell=True)
