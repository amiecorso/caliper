# Parse the HTML reports to generate CSV data

from bs4 import BeautifulSoup
import argparse
import os
import csv

parser = argparse.ArgumentParser(description="Parse HTML reports")
parser.add_argument('--reportpath', default='/home/amie/caliper/experiments/prototest/')
parser.add_argument('--dest', default='/home/amie/caliper/experiments/prototest/results/')
parser.add_argument('--n', default=1)
args = parser.parse_args()


performance_output = args.dest + str(args.n) + "_performance.csv"
resource_output = args.dest + str(args.n) + "_resource.csv"

archival_reports = args.reportpath + "arch_reports/"
if not os.path.isdir(archival_reports):
    os.mkdir(archival_reports)

data = {}
for filename in os.listdir(args.reportpath):
    if filename.startswith("report"):
        htmlfile = open(args.reportpath + filename)
        soup = BeautifulSoup(htmlfile, "lxml")
        tables = soup.find_all("table")
        i = 0
        for table in tables:
            tabledata = []
            rows = table.find_all("tr")
            for row in rows:
                headers = row.find_all("th")
                headers = [ele.text.strip() for ele in headers]
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                if headers:
                    tabledata.append(headers)
                if cols:
                    tabledata.append(cols)
            data[i] = tabledata
            i += 1
        
        htmlfile.close()
        # put the report file in archive folder
        os.rename(args.reportpath + filename, archival_reports + filename)


print(data)

with open(performance_output, 'w') as csvfile:
    writer = csv.writer(csvfile)
    table = data[1] # test with performance metric table
    for row in table:
        writer.writerow(row)

with open(resource_output, 'w') as csvfile:
    writer = csv.writer(csvfile)
    table = data[2]
    for row in table:
        writer.writerow(row)


