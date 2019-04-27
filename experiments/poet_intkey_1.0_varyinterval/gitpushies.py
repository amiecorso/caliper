# gitpushies.py
import subprocess
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--remote_ip")
args = parser.parse_args()

LINUX_PATH = "/home/amie/caliper"
MAC_PATH = "/Users/amiecorso/caliper"
RESULTS_PATH = "/home/amie/results_caliper"

print("gitpushies.py: pushing to github")
command = "cd {} && git add . && git commit -m \"pushing results\" && git push".format(RESULTS_PATH)
command = "ssh amie@{} ".format(args.remote_ip) + "\"" + command + "\""
subprocess.call(command, shell=True)

command = "cd {} && git add . && git commit -m \"pushing from Linux machine\" && git push".format(LINUX_PATH)
command = "ssh amie@{} ".format(args.remote_ip) + "\"" + command + "\""
subprocess.call(command, shell=True)

command = "cd {} && git add . && git commit -m \"pushing from mac\" && git push".format(MAC_PATH)
subprocess.call(command, shell=True)
