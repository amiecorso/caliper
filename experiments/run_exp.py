# Top-level program for generating requisite files and executing experiment

import subprocess

NET_SIZES = [1, 2, 4, 8]
EXP_DIR = "~/caliper/experiments/poet_prototest"
COMPOSE_TEMPLATE = "~/caliper/experiments/templates/sawtooth-poet.yaml"
NETCONFIG_TEMPLATE = "~/caliper/experiments/templates/net_config_template.json"
TPFAMILY = "testTP"
BBFILE = "TestBatchBuilder.js"

# generate compose files
for n in NET_SIZES:
    command = "python compose_file_gen.py --n {} --template {} --dest {}".format(n, COMPOSE_TEMPLATE, EXP_DIR + "/compose_files")
    subprocess.call(command, shell=True)

# generate netconfig files
for n in NET_SIZES:
    command = "python netconfig_file_gen.py --n {} --template {} --dest {} --exp_dir {} --TPfamily {} --bb_file {}".format(n, NETCONFIG_TEMPLATE, EXP_DIR + "/net_config_files", EXP_DIR, TPFAMILY, BBFILE)
    subprocess.call(command, shell=True)

# deliver workload to each network


