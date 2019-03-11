# Top-level program for generating requisite files and executing experiment

import subprocess
import os
import shutil

NET_SIZES = [4]
EXP_DIR = os.getcwd() + "/" # THIS should be the experimental directory
COMPOSE_TEMPLATE = EXP_DIR + "poet-intkey-1.0_template.yaml"
NETCONFIG_TEMPLATE = "~/caliper/experiments/templates/netconfig_template.json"
TPFAMILY = "intkey"
BBFILE = "IntKeyBatchBuilder.js"

# Should this be a command-line option? with default argument?
BENCHCONFIG = EXP_DIR + [f for f in os.listdir(EXP_DIR) if f.endswith(".yaml")][0] # auto-detect benchmark config file in exp_dir
BENCHCONFIG = EXP_DIR + "config-saw-intkey.yaml"

# clear directories:
if os.path.exists(EXP_DIR + "compose_files"):
    shutil.rmtree(EXP_DIR + "compose_files")
if os.path.exists(EXP_DIR + "net_config_files"):
    shutil.rmtree(EXP_DIR + "net_config_files")
if os.path.exists(EXP_DIR + "arch_reports"):
    shutil.rmtree(EXP_DIR + "arch_reports")
if os.path.exists(EXP_DIR + "results"):
    shutil.rmtree(EXP_DIR + "results")
if os.path.exists(EXP_DIR + "LOGS"):
    shutil.rmtree(EXP_DIR + "LOGS")

# generate compose files
print("run_exp.py: generating compose files...")
for n in NET_SIZES:
    command = "python ~/caliper/experiments/compose_file_gen.py --n {} --template {} --dest {}".format(n, COMPOSE_TEMPLATE, EXP_DIR + "/compose_files")
    subprocess.call(command, shell=True)

# generate netconfig files
print("run_exp.py: generating netconfig files...")
for n in NET_SIZES:
    command = "python ~/caliper/experiments/netconfig_file_gen.py --n {} --template {} --dest {} --exp_dir {} --TPfamily {} --bb_file {}".format(n, NETCONFIG_TEMPLATE, EXP_DIR + "/net_config_files", EXP_DIR, TPFAMILY, BBFILE)
    subprocess.call(command, shell=True)
'''
# deliver workload to each network
for n in NET_SIZES:
    base_filename = NETCONFIG_TEMPLATE.split('/')[-1].replace("_template", "") # get rid of 'template' tag
    netconfig = EXP_DIR + "net_config_files/" + str(n) + "_" + base_filename
    command = "node ~/caliper/benchmark/{}/main.js -c {} -n {}".format(TPFAMILY, BENCHCONFIG, netconfig)
    print("run_exp.py: Calling \"" + command + "\"")
    subprocess.call(command, shell=True)

# final data processing
command = "python ~/caliper/experiments/data_scripts/process_exp.py --exp_dir {}".format(EXP_DIR)
subprocess.call(command, shell=True)
'''
