import os
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--exp_dir")
args = parser.parse_args()

if not args.exp_dir.endswith("/"):
    args.exp_dir += "/"

print("cleandirs.py: cleaning directories...")
if os.path.exists(args.exp_dir + "compose_files"):
    shutil.rmtree(args.exp_dir + "compose_files")
if os.path.exists(args.exp_dir + "net_config_files"):
    shutil.rmtree(args.exp_dir + "net_config_files")
if os.path.exists(args.exp_dir + "arch_reports"):
    shutil.rmtree(args.exp_dir + "arch_reports")
if os.path.exists(args.exp_dir + "results"):
    shutil.rmtree(args.exp_dir + "results")
if os.path.exists(args.exp_dir + "LOGS"):
    shutil.rmtree(args.exp_dir + "LOGS")
