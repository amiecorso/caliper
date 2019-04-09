# Automate some network examinations on running Sawtooth instance (Docker)

import docker
import time
import datetime
import argparse
import os

parser = argparse.ArgumentParser(description="Parse validator logs for stale block rate")
parser.add_argument('--n', default=1, type=int, help="Network size")
parser.add_argument('--dest', default='/home/amie/caliper/experiments/data_scripts/', help="Where parsing results should be stored")
parser.add_argument('--run_num', default="only", help="Index identical experimental runs")
parser.add_argument('--rest_url', default='http://sawtooth-rest-api-0:8008', help="URL of a rest-api container for this network") # defaults to size 1 network
parser.add_argument('--val_name', default ='sawtooth-validator', help="base name for validator containers") # default to size 1 network
parser.add_argument('--shell_name', default='sawtooth-shell-default', help="name of shell container")
parser.add_argument('--single', default=False, action='store_const', const=True,  help="Include this flag if val_name should be left un-appended")
args = parser.parse_args()

INTERVAL = 5.0 # number of seconds between updates
REPEATS = 8
PRINT = True

if not args.dest.endswith("/"):
    args.dest += "/"
args.dest = args.dest + str(args.n) + "/"
if not os.path.exists(args.dest):
    os.mkdir(args.dest)

output_file = args.dest + str(args.n) + "_analysis_run" + args.run_num + ".txt"

def list_blocks():
    blocks = shell.exec_run("sawtooth block list --url " + args.rest_url)
    blocks = blocks[1].decode('utf-8')
    return blocks

def count_blocks():
    blocklist = list_blocks()
    if PRINT:
        print("Block list: \n", blocklist)
    blocklistsplit = blocklist.split('\n')
    numblocks = len(blocklistsplit) - 3 # 2 for header and 1 initial settings block
    #print("Total num blocks (not settings): ", numblocks)
    return numblocks

def count_txns():
    txnlist = shell.exec_run("sawtooth transaction list --url " + args.rest_url)
    txnlist = txnlist[1].decode('utf-8')
    txnlistsplit = txnlist.split('\n') 
    numtxns = len(txnlistsplit) - 8 # 2 for header and 6 initial settings txns
    #print("Total num txns: ", numtxns)
    return numtxns

# Give network time to spin up...
time.sleep(25)
network_up = False
while not network_up:
    try:
        docker_client = docker.from_env()
        shell = docker_client.containers.get(args.shell_name)
        network_up = True
    except:
        "analyze_network.py: Waiting for Docker network..."
        time.sleep(1)

# perform updates every X seconds
out = open(output_file, "w")
header = "Datetime\t Elapsed\t Num Blocks\t Num Txns\n"
out.write(header)
if PRINT:
    print(header)

starttime=time.time()
while True:
    if REPEATS:
        elapsed = round((time.time() - starttime), 2)
        now = datetime.datetime.now()
        num_blocks = count_blocks()
        num_txns = count_txns()
        data = "{}\t {}\t {}\t {}\n".format(now, elapsed, num_blocks, num_txns)
        out.write(data)
        if PRINT:
            print(data, end='')
        time.sleep(INTERVAL - ((time.time() - starttime) % INTERVAL))
    else:
        break
    REPEATS -= 1

blocks = list_blocks()
out.write("\n\n" + blocks)
if PRINT:
    print("Block list main chain: \n", blocks)

out.close()
