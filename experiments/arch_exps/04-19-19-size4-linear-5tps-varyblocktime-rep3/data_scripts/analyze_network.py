# Automate some network examinations on running Sawtooth instance (Docker)

import docker
import time
import datetime
import math
import argparse
import os
import sys

parser = argparse.ArgumentParser(description="Parse validator logs for stale block rate")
parser.add_argument('--n', default=1, type=int, help="Network size")
parser.add_argument('--dest', default='/home/amie/caliper/experiments/data_scripts/', help="Where parsing results should be stored")
parser.add_argument('--run_num', default="only", help="Index identical experimental runs")
parser.add_argument('--rest_url', default='http://sawtooth-rest-api-0:8008', help="URL of a rest-api container for this network") # defaults to size 1 network
parser.add_argument('--val_name', default ='sawtooth-validator', help="base name for validator containers") # default to size 1 network
parser.add_argument('--shell_name', default='sawtooth-shell-default', help="name of shell container")
parser.add_argument('--single', default=False, action='store_const', const=True,  help="Include this flag if val_name should be left un-appended")
parser.add_argument('--time', default=30, help="How long to run this script")
parser.add_argument('--tps')
parser.add_argument('--interval')
args = parser.parse_args()

INTERVAL = 5.0 # number of seconds between updates
WAIT = 20
MAXTIME = int(args.time) + WAIT
START = time.time()
PRINT = True
#PRINT = False
PRINTBLOCKLIST = False


if not args.dest.endswith("/"):
    args.dest += "/"
args.dest = args.dest + str(args.n) + "/"
if not os.path.exists(args.dest):
    os.mkdir(args.dest)
args.dest = args.dest + str(args.tps) + "tps/"
if not os.path.exists(args.dest):
    os.mkdir(args.dest)
args.dest = args.dest + str(args.interval) + "sec/"
if not os.path.exists(args.dest):
    os.mkdir(args.dest)

output_file = args.dest + str(args.n) + "_analysis_run" + args.run_num + ".txt"

def list_blocks():
    try:
        blocks = shell.exec_run("sawtooth block list --url " + args.rest_url)
    except:
        print("Shell container not available... Exiting gracefully.")
        return None
    blocks = blocks[1].decode('utf-8')
    return blocks


def count_blocks():
    blocklist = list_blocks()
    if PRINTBLOCKLIST:
        print("Block list: \n", blocklist)
    blocklistsplit = blocklist.split('\n')
    numblocks = len(blocklistsplit) - 3 # 2 for header and 1 initial settings block
    #print("Total num blocks (not settings): ", numblocks)
    return numblocks

def count_txns():
    try:
        txnlist = shell.exec_run("sawtooth transaction list --url " + args.rest_url)
    except:
        print("Shell container not available... Exiting gracefully.")
        return None
    txnlist = txnlist[1].decode('utf-8')
    txnlistsplit = txnlist.split('\n') 
    numtxns = len(txnlistsplit) - 2 # 2 for header lines
    #print("Total num txns: ", numtxns)
    return numtxns

# Give network time to spin up...
# and also make sure we've waited at least 15 seconds?
now = time.time()
network_up = False
while not network_up:
    try:
        docker_client = docker.from_env()
        shell = docker_client.containers.get(args.shell_name)
        network_up = True
    except:
        current_time = time.time()
        if (current_time - START) > MAXTIME:
            print("analyze_network.py: Timed out waiting for network to come up... waited {} seconds. Exiting.".format(MAXTIME))
            sys.exit()
        "analyze_network.py: Waiting for Docker network..."
        time.sleep(1)

newtime = time.time()
waited = newtime - now
if waited < WAIT:
    time.sleep(WAIT - waited)

# get network settings
settings = shell.exec_run("sawtooth settings list --url " + args.rest_url)[1].decode('utf-8')
# block-tracking infrastructure:
SEEN = set()
TIMESTAMPED = []
header = "\nDATETIME\t " + "ELAPSED\t " + list_blocks().split('\n')[0] + "\n"
TIMESTAMPED.append(header)

# perform updates every X seconds
out = open(output_file, "w")
header = "Datetime\t Elapsed\t Num Blocks\t Num Txns\n"
out.write(header)
if PRINT:
    print(header)

last_good_blocks = "last_good_blocks = none"
last_num_txns = 0

starttime=time.time()
while True:
    try:
        shell = docker_client.containers.get(args.shell_name)
    except: # break loop as soon as network comes down?? don't want to wait a little longer? make some record in the log and then keep going?
        break
    # OR after MAXTIME has elapsed
    current = time.time()
    if (current - START) > MAXTIME:
        break
    elapsed = round((time.time() - starttime), 2)
    now = datetime.datetime.now()
    blocks = list_blocks()
    if not blocks:
        blocks = last_good_blocks
        break # means the shell container is already down, but we still want to write our outputs
    else:
        last_good_blocks = blocks
    splitblocks = blocks.split('\n')
    num_blocks = len(splitblocks) - 2# one for header and one for the weird space at the end
    num_txns = count_txns()
    if num_txns is None:
        num_txns = last_num_txns
        break # shell container already dowon, but we still want to write our outputs
    else:
        last_num_txns = num_txns
    data = "{}\t {}\t {}\t {}\n".format(now, elapsed, num_blocks, num_txns)
    out.write(data)
    if PRINT:
        print(data, end='')
    # process for uniqueness
    splitblocks = splitblocks[1:-1]
    splitblocks.reverse()
    for entry in splitblocks:
        blockID = entry.split()[1]
        entry = " ".join(entry.split()[:-1])
        if blockID not in SEEN:
            SEEN.add(blockID)
            TIMESTAMPED.append(str(now) + " " + str(elapsed) + " " + entry + "\n")

    time.sleep(INTERVAL - ((time.time() - starttime) % INTERVAL))

out.writelines(TIMESTAMPED)
out.write("\n\n" + last_good_blocks)
out.write("\n\nOn-chain Settings:\n" + settings)
if PRINT:
    for line in TIMESTAMPED:
        print(line, end="")
    print("Block list main chain: \n", last_good_blocks)

out.close()
