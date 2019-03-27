# Parse the HTML reports to generate CSV data

from bs4 import BeautifulSoup
import argparse
import os
import csv
import time

reportpath = "./"
n = 1
dest = "./"

performance_output = "performance.csv"
resource_output = "resource.csv"

data = {}
for filename in os.listdir(reportpath):
    if filename.startswith("report"):
        htmlfile = open(reportpath + filename)
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


print(data)
print(data[0])
#print(data[1])

try:
    with open(performance_output, 'w') as csvfile:
        writer = csv.writer(csvfile)
        table = data[0] # test with performance metric table
        for row in table:
            writer.writerow(row)

    with open(resource_output, 'w') as csvfile:
        writer = csv.writer(csvfile)
        table = data[2]
        for row in table:
            writer.writerow(row)
except:
    print("Error while parsing html report...  Data dictionary: ", data)

