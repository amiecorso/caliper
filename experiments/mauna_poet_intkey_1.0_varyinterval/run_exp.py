# Top-level program for generating requisite files and executing experiment

import subprocess
import os
import shutil
import time

# Naming scheme: date, workloads/durations, rate controller, network sizes, repeats, ..??? the thing we're testing??
# auto-generate this?
#REMOTEIP = "192.168.0.105"
REMOTEIP = "128.223.6.92"
SAVE_AS = time.strftime("%m-%d-%y") + "sshtesting"
#NET_SIZES = [1, 2, 4, 8]
#REPEATS = 2
#INTERVALS = [3, 5, 10, 20, 30, 40, 50, 60, 80, 100]
NET_SIZES = [1]
REPEATS = 1
INTERVALS = [20]
TIME = 60
#           (TPS, duration, unfinished)
#WORKLOADS = [(5, 800, 200), (10, 800, 200), (15, 800, 200), (20, 800, 200), (30, 800, 200), (40, 800, 200), (50, 800, 200), (60, 800, 200)]
#WORKLOADS = [(5, 800, 200), (10, 800, 200), (15, 800, 200), (20, 800, 200), (25, 800, 200), (30, 800, 200), (40, 800, 200)]
WORKLOADS = [(5, 40, 5)]
#TIME = 2000 # maximum time to run external monitor... should at least be as long as the duration of experiment, otherwise monitor will come down early
LEAVE_UP = False
if LEAVE_UP: # if leaving the network running, can only handle one instance at a time
    NET_SIZES = [1]
    REPEATS = 1
#TARGET_WAIT = 20
# ON remote machine
EXP_DIR = "/home/amie/caliper/experiments/poet_intkey_1.0_varyinterval/"
THIS_DIR = os.getcwd() + "/"
COMPOSE_TEMPLATE = EXP_DIR + "templates/poet-intkey-1.0_template_SMALLNETWORK.yaml"
#COMPOSE_TEMPLATE = EXP_DIR + "templates/poet-intkey-1.0_template.yaml"
NETCONFIG_TEMPLATE = "./templates/netconfig_template.json"
#BENCHCONFIG_TEMPLATE = "./templates/config-saw-intkey-TEMPLATE-FFR.yaml"
BENCHCONFIG_TEMPLATE = "./templates/config-saw-intkey-TEMPLATE-LINEAR.yaml"
TPFAMILY = "intkey"
BBFILE = "IntKeyBatchBuilder.js"
#BENCHCONFIG = EXP_DIR + [f for f in os.listdir(EXP_DIR) if f.endswith(".yaml")][0] # auto-detect benchmark config file in exp_dir
BENCHCONFIG = THIS_DIR + "config-saw-intkey.yaml"

# Clean directories, both local and remote
subprocess.call("python3 ./cleandirs.py --exp_dir {}".format(THIS_DIR), shell=True)
subprocess.call("ssh amie@{} \"python3 {}cleandirs.py --exp_dir {}\"".format(REMOTEIP, EXP_DIR, EXP_DIR), shell=True)

# deliver workload to each network
for n in NET_SIZES:
    for interval in INTERVALS:
        # generate compose files
        initial_wait_time = interval * n # initial_wait = target_wait * pop_size
        command = "\"python {}generators/compose_file_gen.py --n {} --template {} --dest {} --target_wait_time {} --initial_wait_time {}\"".format(EXP_DIR, n, COMPOSE_TEMPLATE, EXP_DIR + "compose_files", interval, initial_wait_time)
        command = "ssh " + "amie@" + REMOTEIP + " " + command
        print("executing command: ", command)
        subprocess.call(command, shell=True)
        for load in WORKLOADS:
            tps, duration, unfinished = load
            # generate benchconfig file
            command = "python ./generators/benchconfig_file_gen.py --exp_dir {} --template {} --tps {} --duration {} --unfinished {} --txnsperbatch {} --label {}".format(THIS_DIR, BENCHCONFIG_TEMPLATE, tps, duration, unfinished, 20, str(tps) + "TPS" + str(interval) + "sec")
            subprocess.call(command, shell=True)

            for repeat in range(REPEATS):
                # generate netconfig file
                command = "python ./generators/netconfig_file_gen.py --n {} --template {} --dest {} --exp_dir {} --TPfamily {} --bb_file {} --run_num {} --leave_up {} --tps {} --interval {} --remoteip {}".format(n, NETCONFIG_TEMPLATE, THIS_DIR + "/net_config_files", EXP_DIR, TPFAMILY, BBFILE, repeat, LEAVE_UP, tps, interval, REMOTEIP)
                subprocess.call(command, shell=True)

                # external monitor:
                analysis = "python3 {}data_scripts/analyze_network.py --n {} --dest {} --run_num {} --time {} --tps {} --interval {} &".format(EXP_DIR, n, EXP_DIR, repeat, TIME, tps, interval)
                analysis = "ssh amie@{} ".format(REMOTEIP) + "\"" + analysis + "\""
                print("Starting external analysis...")
                print("executing command: ", analysis)
                subprocess.Popen(analysis, shell=True)

                # start caliper
                base_filename = NETCONFIG_TEMPLATE.split('/')[-1].replace("_template", "") # get rid of 'template' tag
                netconfig = THIS_DIR + "net_config_files/" + str(n) + "_" + base_filename
                command = "node ~/caliper/benchmark/{}/main.js -c {} -n {}".format(TPFAMILY, BENCHCONFIG, netconfig)
                print("run_exp.py: Calling \"" + command + "\"")
                subprocess.call(command, shell=True)

                # parse reports and copy to remote machine
                print("run_exp.py: Calling report_parser.py")
                parse_reports = "python {}data_scripts/report_parser.py --reportpath {} --results {}results/ --n {} --run_num {} --tps {} --interval {} --remote_dir {} --remote_ip {}".format(THIS_DIR, THIS_DIR, THIS_DIR, n, repeat, tps, interval, EXP_DIR, REMOTEIP)
                subprocess.call(parse_reports, shell=True)


#TODO: the rest of this needs to be scp/ssh
# Move Caliper Logs to this directory
'''
log_dir = EXP_DIR + "/LOGS"
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
caliper_logs = log_dir + "/caliperlogs"
if not os.path.exists(caliper_logs):
    os.mkdir(caliper_logs)

original_logs = "/home/amie/caliper/log/"
for fname in os.listdir(original_logs):
    shutil.move(original_logs + fname, caliper_logs)

'''
# final data processing
command = "ssh amie@{} \"python {}/data_scripts/process_exp.py --exp_dir {}\"".format(REMOTEIP, EXP_DIR, EXP_DIR)
subprocess.call(command, shell=True)

# copy experimental directory into archival directory
command = "ssh amie@{} \"python {}savexp.py --save_as {} --exp_dir {}\"".format(REMOTEIP, EXP_DIR, SAVE_AS, EXP_DIR) 
subprocess.call(command, shell=True)

# Clean directories, both local and remote
subprocess.call("python3 ./cleandirs.py --exp_dir {}".format(THIS_DIR), shell=True)
subprocess.call("ssh amie@{} \"python3 {}cleandirs.py --exp_dir {}\"".format(REMOTEIP, EXP_DIR, EXP_DIR), shell=True)

command = "python gitpushies.py --remote_ip {}".format(REMOTEIP) 
subprocess.call(command, shell=True)
