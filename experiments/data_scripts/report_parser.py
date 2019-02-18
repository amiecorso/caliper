# Parse the HTML reports to generate CSV data

from bs4 import BeautifulSoup
import argparse
import os

parser = argparse.ArgumentParser(description="Parse HTML reports")
parser.add_argument('--reportpath', default='/home/amie/caliper/experiments/prototest')
parser.add_argument('--dest', default='home/amie/caliper/experiments/prototest/results/')
parser.add_argument('--netsize', default=1)
args = parser.parse_args()

print(args)

output_file = args.dest + "summary_" + args.netsize + ".csv"

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
                    print("got a header row")
                    tabledata.append(headers)
                if cols:
                    print("got a cols row")
                    tabledata.append(cols)
            data[i] = tabledata
            i += 1
        
        htmlfile.close()

print(data)


