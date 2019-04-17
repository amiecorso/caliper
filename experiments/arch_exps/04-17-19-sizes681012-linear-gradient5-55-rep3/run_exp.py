# Top-level program for generating requisite files and executing experiment

import subprocess
import os
import shutil
import time

# Naming scheme: date, workloads/durations, rate controller, network sizes, repeats, ..??? the thing we're testing??
# auto-generate this?
SAVE_AS = time.strftime("%m-%d-%y") + "-sizes681012-linear-gradient5-55-rep3"
NET_SIZES = [6, 8, 10, 12]
REPEATS = 3
#           (TPS, duration, unfinished)
WORKLOADS = [(5, 1000, 200), (10, 1000, 200), (15, 1000, 200), (20, 1000, 200), (25, 1000, 200), (30, 1000, 200), (35, 1000, 200), (40, 1000, 200), (45, 1000, 200), (50, 1000, 200), (55, 1000, 200)]
#WORKLOADS = [(5, 10, 5)]
TIME = 2000 # maximum time to run external monitor... should at least be as long as the duration of experiment, otherwise monitor will come down early
LEAVE_UP = False
if LEAVE_UP: # if leaving the network running, can only handle one instance at a time
    NET_SIZES = [1]
    REPEATS = 1
TARGET_WAIT = 20
EXP_DIR = os.getcwd() + "/" # THIS should be the experimental directory
COMPOSE_TEMPLATE = EXP_DIR + "templates/poet-intkey-1.0_template_SMALLNETWORK.yaml"
#COMPOSE_TEMPLATE = EXP_DIR + "templates/poet-intkey-1.0_template.yaml"
NETCONFIG_TEMPLATE = "./templates/netconfig_template.json"
#BENCHCONFIG_TEMPLATE = "./templates/config-saw-intkey-TEMPLATE-FFR.yaml"
BENCHCONFIG_TEMPLATE = "./templates/config-saw-intkey-TEMPLATE-LINEAR.yaml"
TPFAMILY = "intkey"
BBFILE = "IntKeyBatchBuilder.js"
#BENCHCONFIG = EXP_DIR + [f for f in os.listdir(EXP_DIR) if f.endswith(".yaml")][0] # auto-detect benchmark config file in exp_dir
BENCHCONFIG = EXP_DIR + "config-saw-intkey.yaml"
'''
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


# deliver workload to each network
for n in NET_SIZES:
    # generate compose files
    initial_wait_time = TARGET_WAIT * n # initial_wait = target_wait * pop_size
    command = "python ./generators/compose_file_gen.py --n {} --template {} --dest {} --target_wait_time {} --initial_wait_time {}".format(n, COMPOSE_TEMPLATE, EXP_DIR + "/compose_files", TARGET_WAIT, initial_wait_time)
    subprocess.call(command, shell=True)

    for load in WORKLOADS:
        # generate benchconfig file
        tps, duration, unfinished = load
        command = "python ./generators/benchconfig_file_gen.py --exp_dir {} --template {} --tps {} --duration {} --unfinished {} --txnsperbatch {} --label {}".format(EXP_DIR, BENCHCONFIG_TEMPLATE, tps, duration, unfinished, 20, str(tps) + "TPS")
        subprocess.call(command, shell=True)

        for repeat in range(REPEATS):
            # generate netconfig file
            command = "python ./generators/netconfig_file_gen.py --n {} --template {} --dest {} --exp_dir {} --TPfamily {} --bb_file {} --run_num {} --leave_up {} --tps {}".format(n, NETCONFIG_TEMPLATE, EXP_DIR + "/net_config_files", EXP_DIR, TPFAMILY, BBFILE, repeat, LEAVE_UP, tps)
            subprocess.call(command, shell=True)
            # this could use some cleaning up?

            # external monitor:
            analysis_dest = EXP_DIR + "results" + "/"
            if not os.path.exists(analysis_dest):
                os.mkdir(analysis_dest)
            analysis = "python3 ./data_scripts/analyze_network.py --n {} --dest {} --run_num {} --time {} --tps {} &".format(n, analysis_dest, repeat, TIME, tps)
            print("Starting external analysis...")
            print("executing command: ", analysis)
            subprocess.Popen(analysis, shell=True)
            
            base_filename = NETCONFIG_TEMPLATE.split('/')[-1].replace("_template", "") # get rid of 'template' tag
            netconfig = EXP_DIR + "net_config_files/" + str(n) + "_" + base_filename
            command = "node ~/caliper/benchmark/{}/main.js -c {} -n {}".format(TPFAMILY, BENCHCONFIG, netconfig)
            print("run_exp.py: Calling \"" + command + "\"")
            subprocess.call(command, shell=True)
'''
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


# final data processing
command = "python ./data_scripts/process_exp.py --exp_dir {}".format(EXP_DIR)
subprocess.call(command, shell=True)

# copy experimental directory into archival directory
index = 1
while os.path.exists("/home/amie/caliper/experiments/arch_exps/{}".format(SAVE_AS)):
    SAVE_AS = SAVE_AS + str(index)
    index += 1
print("run_exp.py: Saving experiment as \"{}\"".format(SAVE_AS))
command = "cp -r {} /home/amie/caliper/experiments/arch_exps/{}".format(EXP_DIR, SAVE_AS)
subprocess.call(command, shell=True)

# git push the whole thing
print("run_exp.py: Pushing to GitHub...")
os.chdir("/home/amie/caliper/")
command = "git add . && git commit -m \"saving exp {}\" && git push".format(SAVE_AS)
subprocess.call(command, shell=True)
