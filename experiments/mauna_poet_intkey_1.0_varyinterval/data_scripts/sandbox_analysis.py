# analyze analysis files and write data

FILE = "./analysis.txt"

data = []
with open(FILE, 'r') as f:
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
throughput = numtxns/duration

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
print("numblocks: ", numblocks)
print("numtxns: ", numtxns)
print("round duration: ", duration, "seconds")
print("throughput: ", throughput, " TPS")
print("avgerage interval: ", avg_interval, " seconds")
print("min interval: ", min_interval, " seconds")
print("max interval: ", max_interval, " seconds")


