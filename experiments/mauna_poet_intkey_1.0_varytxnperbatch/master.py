import subprocess

txnsperbatch = [20, 40, 100, 200]

for tpb in txnsperbatch:
    subprocess.call("python3 run_exp.py --tperb {}".format(tpb), shell=True)


