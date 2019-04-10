# Process folder of experimental result files into single CSV

import argparse
import os
import sys

parser = argparse.ArgumentParser(description="Process folder of experimental result files into single CSV")
parser.add_argument('--exp_dir', help="The path to experiment")
args = parser.parse_args()

results_dir = args.exp_dir.rstrip("/") + "/results/"
run_exp_path = args.exp_dir.rstrip("/") + "/run_exp.py"
PERFORMANCE_SUMMARY = results_dir + "/performance_summary.csv"
RESOURCE_SUMMARY = results_dir + "/resource_summary.csv"


with open(run_exp_path, 'r') as run_exp:
    contents = run_exp.readlines()

# determine number of runs
for line in contents:
    if "REPEATS" in line:
        REPEATS = int(line.split("=")[-1].strip())
        break

# Traverse directory tree, read relevant files and incorporate extra information
for size in os.listdir(results_dir):
    sizedir = results_dir + size
    for tps in os.listdir(sizedir):
        rate = tps.rstrip('tps')
        tpsdir = sizedir + "/"  + tps
        for datafile in os.listdir(tpsdir):
            for run in range(REPEATS):

performance_files = [f for f in os.listdir(results_dir) if "performance" in f]
resource_files = [f for f in os.listdir(results_dir) if "resource" in f]
staleb_files = [f for f in os.listdir(results_dir) if "stale" in f]

if not performance_files:
    sys.exit("Error: there are no results")

# process performance files
os.chdir(results_dir)
perf_out = open(PERFORMANCE_SUMMARY, "w")
    # write header
with open(performance_files[0], 'r') as f:
    perf_out.write("Network Size,Stale Block Rate," + f.readline())

for num in netsizes:
    pfile = [f for f in performance_files if f.startswith(num)][0]
    sbfile = [f for f in staleb_files if f.startswith(num)][0]
    with open(pfile, 'r') as f:
        perf_lines = f.readlines()
    with open(sbfile, 'r') as f:
        sb_data = f.readlines()[0] # get just the block rate, ignore block list diagnostics
    line = ",".join([num, sb_data.strip(), perf_lines[-1]])
    perf_out.write(line)

perf_out.close()

# process resource consumption files
resource_out = open(RESOURCE_SUMMARY, 'w')
    # write header
with open(resource_files[0], 'r') as f:
    resource_out.write("Network Size," + f.readline())

for num in netsizes:
    resfile = [f for f in resource_files if f.startswith(num)][0]
    with open(resfile, 'r') as f:
        f.readline() # move past header
        res_lines = f.readlines() # read the rest
    for line in res_lines:
        resource_out.write(num + "," + line)
resource_out.close()


