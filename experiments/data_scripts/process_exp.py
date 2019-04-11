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
                    perf_out.write("Network Size,Run Index," + f.readline().rstrip('\n') + ",Stale Block Rate," + "Num Blocks," + "Num Txns," + "Round Duration," + "My Throughput," +  "Avg Interval," + "Min Interval," + "Max Interval," + "PercentDiff on TPS\n")
                    print("made it past write")
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
            # process PERFORMANCE file + STALE BLOCK file
            pfile = [f for f in performance_files if f.endswith(str(run) + ".csv")][0]
            sbfile = [f for f in staleb_files if f.endswith(str(run) + ".csv")][0]
            afile = [f for f in analysis_files if f.endswith(str(run) + ".txt")][0]
            with open(pfile, 'r') as f:
                perf_lines = f.readlines()
            with open(sbfile, 'r') as f:
                sb_data = f.readlines()[0] # get just the block rate, ignore block list diagnostics
            outputline = ",".join([size, str(run), perf_lines[-1].rstrip('\n'), str(round(float(sb_data.strip()), 3))]) #<-- only handles a ONE-line perf (one round)
            # process ANALYSIS file
            data = []
            with open(afile, 'r') as f:
                f.readline() # read header (Datetime, Elapsed, Num Blocks, Num Txns)
                line = f.readline()
                while line != "\n":
                    data.append(line)
                    line = f.readline()

            data = [entry.strip().split("\t ") for entry in data]
            data = [[entry[0], round(float(entry[1]), 1), int(entry[2]), int(entry[3])] for entry in data]
            data = data[1:-4] # cut off the GENESIS BLOCK and the end of the round that the monitor goes over
            print(data)

            numblocks = data[-1][2]
            numtxns = data[-1][3]
            duration = data[-1][1]
            throughput = round(numtxns/duration, 1)

            blockdata = {}
            prev_publish_time = 0
            prev_total_txns = 0
            current_block = data[0][2]
            publish_time = data[0][1]
            total_txns = data[0][3]
            time_since_last = publish_time - prev_publish_time
            txns_in_block = total_txns - prev_total_txns
            blockdata[current_block] = (publish_time, txns_in_block, time_since_last)
            prev_publish_time = publish_time
            prev_total_txns = total_txns
            for i in range(len(data)):
                this_block = data[i][2]
                if current_block != this_block:
                    # process previous block's txns:
                    total_txns = data[i - 1][3]
                    txns_in_block = total_txns - prev_total_txns
                    # write data for prev block
                    blockdata[current_block] = (publish_time, txns_in_block, time_since_last)
                    prev_total_txns = total_txns

                    # move on and start processing for next block
                    current_block = this_block
                    publish_time = data[i][1]
                    time_since_last = publish_time - prev_publish_time
                    prev_publish_time = publish_time
                    prev_total_txns = total_txns


            print(blockdata)
            # calculate avg block interval
            intervals = []
            for block in blockdata:
                intervals.append(blockdata[block][2])
            avg_interval = round(sum(intervals) / len(intervals), 1)
            min_interval = min(intervals)
            max_interval = max(intervals)

            
            #combine data with Caliper report data
            outputline = ",".join([outputline, str(numblocks), str(numtxns), str(duration), str(throughput), str(avg_interval), str(min_interval), str(max_interval)])
            perf_out.write(outputline + "\n")
            # process resource files for this round
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
