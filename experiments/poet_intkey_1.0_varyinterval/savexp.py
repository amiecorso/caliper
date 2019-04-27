import argparse
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument("--save_as")
parser.add_argument("--exp_dir")
args = parser.parse_args()

SAVE_IN = "/home/amie/caliper/results_caliper"
SAVE_AS = args.save_as
EXP_DIR = args.exp_dir

index = 1
while os.path.exists("{}/{}".format(SAVE_IN, SAVE_AS)):
    SAVE_AS = SAVE_AS + str(index)
    index += 1
print("run_exp.py: Saving experiment as \"{}\"".format(SAVE_AS))
command = "cp -r {} {}/{}".format(EXP_DIR, SAVE_IN, SAVE_AS)
subprocess.call(command, shell=True)
