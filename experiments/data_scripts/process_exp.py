# Process folder of experimental result files into single CSV

import argparse
import os
import sys

parser = argparse.ArgumentParser(description="Process folder of experimental result files into single CSV")
parser.add_argument('--exp_dir', help="The path to experiment")
args = parser.parse_args()

results_dir = args.exp_dir.rstrip("/") + "/results/"
run_exp_path = args.exp_dir.rstrip("/") + "/run_exp.py"
PERFORMANCE_SUMMARY = results_dir + "performance_summary.csv"
RESOURCE_SUMMARY = results_dir + "resource_summary.csv"

with open(run_exp_path, 'r') as run_exp:
    contents = run_exp.readlines()

# determine REPEATS and NETSIZES from run_exp.py
for line in contents:
    if "REPEATS" in line:
        REPEATS = int(line.split("=")[-1].strip())
        break
for line in contents:
    if "NET_SIZES" in line:
        NET_SIZES = line.split("=")[-1].strip().strip("[").strip("]").split(",")
        break
for i in range(len(NET_SIZES)):
    NET_SIZES[i] = NET_SIZES[i].strip()
NET_SIZES.sort(key=int)
# Open summary files and write headers:
perf_out = open(PERFORMANCE_SUMMARY, "w")
resource_out = open(RESOURCE_SUMMARY, 'w')
pheader = False
rheader = False
# Traverse directory tree, read relevant files and incorporate extra information
for size in NET_SIZES:
    sizedir = results_dir + size
    rates = os.listdir(sizedir)
    rates = [rate.rstrip("tps") for rate in rates]
    rates.sort(key=int)
    for tps in rates:
        tpsdir = sizedir + "/"  + tps + "tps/"
        performance_files = [tpsdir + f for f in os.listdir(tpsdir) if "performance" in f]
        resource_files = [tpsdir + f for f in os.listdir(tpsdir) if "resource" in f]
        staleb_files = [tpsdir + f for f in os.listdir(tpsdir) if "stale" in f]
        analysis_files = [tpsdir + f for f in os.listdir(tpsdir) if "analysis" in f]
        # Write headers
        try:
            if not pheader:
                with open(performance_files[0], 'r') as f:
                    perf_out.write("Network Size,Run Index," + f.readline().rstrip('\n') + ",Stale Block Rate\n")
            pheader = True
        except Exception as e:
            print(e)
            print("Error: missing Performance results?")
            sys.exit()
        try:
            if not rheader:
                with open(resource_files[0], 'r') as f:
                    resource_out.write("Network Size," + f.readline())
            rheader = True
        except Exception as e:
            print(e)
            print("Error: missing Performance results?")
            sys.exit()

        '''
        print(performance_files)
        print(resource_files)
        print(staleb_files)
        print(analysis_files)
        '''
        for run in range(REPEATS):
            # process performance files + stale block files
            pfile = [f for f in performance_files if f.endswith(str(run) + ".csv")][0]
            sbfile = [f for f in staleb_files if f.endswith(str(run) + ".csv")][0]
            with open(pfile, 'r') as f:
                perf_lines = f.readlines()
            with open(sbfile, 'r') as f:
                sb_data = f.readlines()[0] # get just the block rate, ignore block list diagnostics
            line = ",".join([size, str(run), perf_lines[-1].rstrip('\n'), str(round(float(sb_data.strip()), 3))]) #<-- only handles a ONE-line perf (one round)
            perf_out.write(line + "\n")
            # process resource files for this round
            # TODO: eventually incorporate analysis files too
'''
# process resource consumption files
for num in netsizes:
    resfile = [f for f in resource_files if f.startswith(num)][0]
    with open(resfile, 'r') as f:
        f.readline() # move past header
        res_lines = f.readlines() # read the rest
    for line in res_lines:
        resource_out.write(num + "," + line)
'''
perf_out.close()
resource_out.close()
