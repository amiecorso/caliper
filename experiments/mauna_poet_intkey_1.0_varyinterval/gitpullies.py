# gitpushies.py
import subprocess
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--remote_ip")
parser.add_argument("--exp_dir")
args = parser.parse_args()

LINUX_PATH = "/home/amie/caliper"
#MAC_PATH = "/Users/amiecorso/caliper"
MAC_PATH = "/Users/acorso/caliper"
RESULTS_PATH = "/home/amie/results_caliper"

print("gitpullies.py: pushing to github from mac")
command = "cd {} && git add . && git commit -m \"pushing from mac\" && git push".format(MAC_PATH)
subprocess.call(command, shell=True)

print("gitpulles.py: pulling from github on linux")
'''
command = "cd {} && git add . && git commit -m \'pushing from Linux machine\' && git push".format(LINUX_PATH)
command = "ssh amie@{} ".format(args.remote_ip) + "\"" + command + "\""
subprocess.call(command, shell=True)
'''

command = "cd {} && git pull".format(LINUX_PATH)
command = "ssh amie@{} ".format(args.remote_ip) + "\"" + command + "\""
subprocess.call(command, shell=True)

command = "cd {} && git pull".format(MAC_PATH)
subprocess.call(command, shell=True)

os.chdir(args.exp_dir)
