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
        intervals = os.listdir(tpsdir)
        intervals = [interval.rstrip("sec") for interval in intervals]
        for interval in intervals:
            intdir = tpsdir + interval + "sec/"
            performance_files = [intdir + f for f in os.listdir(intdir) if "performance" in f]
            resource_files = [intdir + f for f in os.listdir(intdir) if "resource" in f]
            staleb_files = [intdir + f for f in os.listdir(intdir) if "stale" in f]
            analysis_files = [intdir + f for f in os.listdir(intdir) if "analysis" in f]
            # Write headers
            try:
                if not pheader:
                    with open(performance_files[0], 'r') as f:
                        header = f.readline().rstrip('\n')
                        splitheader = header.split(",")
                        splitheader[4] = splitheader[4] + " (tps)"
                        splitheader[5] = splitheader[5] + " (s)"
                        splitheader[6] = splitheader[6] + " (s)"
                        splitheader[7] = splitheader[7] + " (s)"
                        splitheader[8] = splitheader[8] + " (tps)"
                        header = ",".join(splitheader)
                        perf_out.write("TargetInterval(s),Network Size,Run Index," + header + ",Stale Block Rate," + "Num Blocks," + "Num Txns," + "Round Duration," + "My Throughput (tps)," +  "Avg Interval," + "Min Interval," + "Max Interval," + "PercentDiff on TPS\n")
                pheader = True
            except Exception as e:
                print(e)
                print("Error: missing Performance results?")
                sys.exit()
            try:
                if not rheader:
                    with open(resource_files[0], 'r') as f:
                        header = ",".join(f.readline().split(",")[2:])
                        splitheader = header.split(",")
                        splitheader[1] = splitheader[1] + " (MB)"
                        splitheader[2] = splitheader[2] + " (MB)"
                        splitheader[3] = splitheader[3] + " (%)"
                        splitheader[4] = splitheader[4] + " (%)"
                        splitheader[5] = splitheader[5] + " (MB)"
                        splitheader[6] = splitheader[6] + " (MB)"
                        splitheader[7] = splitheader[7] + " (B)"
                        splitheader[8] = splitheader[8].strip('\n') + " (B)\n"
                        header = ",".join(splitheader)
                        resource_out.write("Network Size,Delivery Rate (TPS),Run Index," + header)
                rheader = True
            except Exception as e:
                print(e)
                print("Error: missing Resource results?")
                sys.exit()

            '''
            print(performance_files)
            print(resource_files)
            print(staleb_files)
            print(analysis_files)
            '''
            for run in range(REPEATS):
                # process PERFORMANCE file + STALE BLOCK file
                try:
                    pfile = [f for f in performance_files if f.endswith(str(run) + ".csv")][0]
                except:
                    print("No performance file for {}, {}tps, run{}".format(size, tps, run))
                    break
                try:
                    sbfile = [f for f in staleb_files if f.endswith(str(run) + ".csv")][0]
                except:
                    print("No stale block file for {}, {}tps, run{}".format(size, tps, run))
                    break
                try:
                    afile = [f for f in analysis_files if f.endswith(str(run) + ".txt")][0]
                except:
                    print("No analysis file for {}, {}tps, run{}".format(size, tps, run))
                    break
                with open(pfile, 'r') as f:
                    perf_line = f.readlines()
                try:
                    perf_line = perf_line[-1].rstrip('\n')
                except Exception as e:
                    print(e)
                    print("perf_line = ", perf_line)
                    print("pfile = ", pfile)
                    break
                split_perf_line = perf_line.split(',')
                split_perf_line = [entry.split()[0] for entry in split_perf_line]
                caliperthroughput = float(split_perf_line[-1]) # gonna need this later for %diff calc
                perf_line = ",".join(split_perf_line)
                with open(sbfile, 'r') as f:
                    sb_data = f.readlines()[0] # get just the block rate, ignore block list diagnostics
                outputline = ",".join([size, str(run), perf_line, str(round(float(sb_data.strip()), 3))]) #<-- only handles a ONE-line perf (one round)
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
                data = data[1:-3] # cut off the GENESIS BLOCK and the end of the round that the monitor goes over

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

                # calculate avg block interval
                intervals = []
                for block in blockdata:
                    intervals.append(blockdata[block][2])
                avg_interval = round(sum(intervals) / len(intervals), 1)
                min_interval = min(intervals)
                max_interval = max(intervals)

                percent_diff = round((caliperthroughput - throughput) / throughput, 2)
                #combine data with Caliper report data
                outputline = ",".join([interval, outputline, str(numblocks), str(numtxns), str(duration), str(throughput), str(avg_interval), str(min_interval), str(max_interval), str(percent_diff)])
                perf_out.write(outputline + "\n")

                # process resource files for this round
                try:
                    rfile = [f for f in resource_files if f.endswith(str(run) + ".csv")][0]
                except:
                    print("No resource file for {}, {}tps, run{}".format(size, tps, run))
                    break

                with open(rfile, 'r') as f:
                    f.readline() # move past header
                    res_lines = f.readlines()
                for line in res_lines:
                    splitline = line.split(",")[2:]
                    name = splitline[0]
                    splitline = splitline[1:]
                    for i in range(len(splitline)):
                        splitline[i] = "".join([c for c in splitline[i] if (c.isdigit() or c == ".")])
                    line = ",".join([size, str(tps), str(run)]) + "," + name + "," + ",".join(splitline) + "\n"
                    resource_out.write(line)

perf_out.close()
resource_out.close()
