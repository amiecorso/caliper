# intkey_end_tasks.py

import subprocess

print("Executing end_tasks.py")
compose_file = "1_dev-intkey.yaml"
exp_dir = "~/caliper/experiments/dev_intkey/"

parse_logs = "python3 ~/caliper/experiments/stale_blocks/parse_logs.py --n 1 --dest {}results/ --rest_url http://sawtooth-rest-api-default:8008 && sleep 10".format(exp_dir)
#subprocess.call(parse_logs, shell=True)

take_down = "docker-compose -f {}compose_files/{} down".format(exp_dir, compose_file)
subprocess.call(take_down, shell=True)

#subprocess.call("docker volume prune -f", shell=True)

parse_reports = "python3 ~/caliper/experiments/data_scripts/report_parser.py --reportpath {} --dest {}results/ --n {}".format(exp_dir, exp_dir, 1)
#subprocess.call(parse_reports, shell=True)
