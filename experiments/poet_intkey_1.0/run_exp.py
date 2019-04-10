# Top-level program for generating requisite files and executing experiment

import subprocess
import os
import shutil
import time

NET_SIZES = [1]
REPEATS = 1
#           (TPS, duration, unfinished)
#WORKLOADS = [(5, 1000, 5), (10, 1000, 5), (15, 1000, 5), (20, 1000, 5), (25, 1000, 5), (30, 1000, 5), (35, 1000, 5), (40, 1000, 5)]
WORKLOADS = [(5, 10, 5), (10, 10, 5)]
TIME = 10000000 # maximum time to run external monitor... should at least be as long as the duration of experiment, otherwise monitor will come down early
LEAVE_UP = False
if LEAVE_UP: # if leaving the network running, can only handle one instance at a time
    NET_SIZES = [1]
    REPEATS = 1
EXP_DIR = os.getcwd() + "/" # THIS should be the experimental directory
COMPOSE_TEMPLATE = EXP_DIR + "poet-intkey-1.0_template.yaml"
NETCONFIG_TEMPLATE = "~/caliper/experiments/templates/netconfig_template.json"
BENCHCONFIG_TEMPLATE = "~/caliper/experiments/templates/config-saw-intkey-TEMPLATE.yaml"
TPFAMILY = "intkey"
BBFILE = "IntKeyBatchBuilder.js"

# Should this be a command-line option? with default argument?

# NOTE: this auto-detects... and then immediately overwrites with the absolute valute "config-saw-intkey.yaml"
BENCHCONFIG = EXP_DIR + [f for f in os.listdir(EXP_DIR) if f.endswith(".yaml")][0] # auto-detect benchmark config file in exp_dir
BENCHCONFIG = EXP_DIR + "config-saw-intkey.yaml"

print("run_exp.py: cleaning directories...")
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

'''
# generate netconfig files
print("run_exp.py: generating netconfig files...")
for n in NET_SIZES:
    command = "python ~/caliper/experiments/netconfig_file_gen.py --n {} --template {} --dest {} --exp_dir {} --TPfamily {} --bb_file {}".format(n, NETCONFIG_TEMPLATE, EXP_DIR + "/net_config_files", EXP_DIR, TPFAMILY, BBFILE)
    subprocess.call(command, shell=True)
'''

# deliver workload to each network
for n in NET_SIZES:
    for load in WORKLOADS:
        # generate benchconfig file
        tps, duration, unfinished = load
        command = "python ~/caliper/experiments/benchconfig_file_gen.py --exp_dir {} --template {} --tps {} --duration {} --unfinished {} --txnsperbatch {} --label {}".format(EXP_DIR, BENCHCONFIG_TEMPLATE, tps, duration, unfinished, 20, str(tps) + " TPS")
        subprocess.call(command, shell=True)

        for repeat in range(REPEATS):
            # generate netconfig file
            command = "python ~/caliper/experiments/netconfig_file_gen.py --n {} --template {} --dest {} --exp_dir {} --TPfamily {} --bb_file {} --run_num {} --leave_up {} --tps {}".format(n, NETCONFIG_TEMPLATE, EXP_DIR + "/net_config_files", EXP_DIR, TPFAMILY, BBFILE, repeat, LEAVE_UP, tps)
            subprocess.call(command, shell=True)
            # this could use some cleaning up?

            # external monitor:
            analysis_dest = EXP_DIR + "results" + "/"
            if not os.path.exists(analysis_dest):
                os.mkdir(analysis_dest)
            analysis = "python3 /home/amie/caliper/experiments/data_scripts/analyze_network.py --n {} --dest {} --run_num {} --time {} &".format(n, analysis_dest, repeat, TIME)
            print("Starting external analysis...")
            print("executing command: ", analysis)
            subprocess.Popen(analysis, shell=True)
            
            base_filename = NETCONFIG_TEMPLATE.split('/')[-1].replace("_template", "") # get rid of 'template' tag
            netconfig = EXP_DIR + "net_config_files/" + str(n) + "_" + base_filename
            command = "node ~/caliper/benchmark/{}/main.js -c {} -n {}".format(TPFAMILY, BENCHCONFIG, netconfig)
            print("run_exp.py: Calling \"" + command + "\"")
            subprocess.call(command, shell=True)
        

# Move Caliper Logs to this directory
log_dir = EXP_DIR + "/LOGS"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
caliper_logs = log_dir + "/caliperlogs"
if not os.path.exists(caliper_logs):
    os.mkdir(caliper_logs)

original_logs = "/home/amie/caliper/log/"
for fname in os.listdir(original_logs):
    shutil.move(original_logs + fname, caliper_logs)


# not ready for final data processing yet
'''
# final data processing
command = "python ~/caliper/experiments/data_scripts/process_exp.py --exp_dir {}".format(EXP_DIR)
subprocess.call(command, shell=True)
'''
