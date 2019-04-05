# Parse the HTML reports to generate CSV data

from bs4 import BeautifulSoup
import argparse
import os
import csv
import time

parser = argparse.ArgumentParser(description="Parse HTML reports")
parser.add_argument('--reportpath', default='/home/amie/caliper/experiments/prototest/')
parser.add_argument('--results', default='/home/amie/caliper/experiments/prototest/results/')
parser.add_argument('--n', default=1)
parser.add_argument('--run_num', default='only')
args = parser.parse_args()

if not os.path.exists(args.results):
    os.mkdir(args.results)
if not args.results.endswith("/"):
    args.results = args.results + "/"

# the actual directory for holding multiple experimental results
dest_dir = args.results + str(args.n) + "/"
if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)


#current_time = str(int(time.time())) # append unique time to each file to prevent overwriting 
# using run number instead
performance_output = dest_dir + str(args.n) + "_performance_" + "run" + str(args.run_num) + ".csv"
resource_output = dest_dir + str(args.n) + "_resource_" + "run" + str(args.run_num) + ".csv"

archival_reports = args.reportpath + "arch_reports/"
if not os.path.isdir(archival_reports):
    os.mkdir(archival_reports)

data = {}
for filename in os.listdir(args.reportpath):
    if filename.startswith("report") and filename.endswith("html"):
        htmlfile = open(args.reportpath + filename)
        soup = BeautifulSoup(htmlfile, "lxml")
        tables = soup.find_all("table")
        i = 0
        roundindex = 0
        for table in tables:
            resourcetable = False
            tabledata = []

            rows = table.find_all("tr")
            for row in rows:
                headers = row.find_all("th")
                headers = [ele.text.strip() for ele in headers]
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                if "Memory(max)" in headers:
                    resourcetable = True
                    headers.insert(0, "round" + str(roundindex))
                if headers:
                    tabledata.append(headers)
                if cols:
                    if resourcetable:
                        cols.insert(0, "round" + str(roundindex))
                    tabledata.append(cols)
            if resourcetable:
                if roundindex > 0:
                    for rowindex in range(1, len(tabledata)):
                        data["resources"].append(tabledata[rowindex])
                else:
                    data["resources"] = tabledata
                roundindex += 1
            else:
                data[i] = tabledata
                i += 1
        
        htmlfile.close()
        # put the report file in archive folder
        os.rename(args.reportpath + filename, archival_reports + str(args.n) + "-report_" + str(int(time.time())) + ".html")


#print(data)
try:
    with open(performance_output, 'w') as csvfile:
        writer = csv.writer(csvfile)
        table = data[0] # first table should be summary table
        for row in table:
            writer.writerow(row)
    with open(resource_output, 'w') as csvfile:
        writer = csv.writer(csvfile)
        table = data["resources"] # is this even right?? resources might not be last table... how to handle resources/round?
        for row in table:
            writer.writerow(row)
except:
    print("Error while parsing html report...  Data dictionary: ", data)

