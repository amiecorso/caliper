import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--f1")
parser.add_argument("--f2")
parser.add_argument("--o")

args = parser.parse_args()

with open(args.f1, 'r') as f1:
    data1 = f1.read()

with open(args.f2, 'r') as f2:
    data2 = f2.readlines()

with open(args.o, 'w') as out:
    out.write(data1)
    out.writelines(data2[1:]) # skip header on file2


