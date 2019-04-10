# benchconfig_file_gen.py

import argparse
import os

parser = argparse.ArgumentParser(description="Generate network configuration file from specified template, pointing to composefile/network of specified size.")
parser.add_argument('--n', default=1, type=int, help="The network size for this Caliper run")
parser.add_argument('--template', default='/home/amie/caliper/experiments/templates/config-saw-intkey-TEMPLATE.yaml', help="The template file from which to create benchmark config file.")
parser.add_argument('--exp_dir', default='/home/amie/caliper/experiments/poet_intkey_1.0', help="The directory of this experiment")
parser.add_argument('--run_num', default="only", help="The repeat we're on, for performing identical runs of same workload")
parser.add_argument('--tps', default=10)
parser.add_argument('--duration', default=30)
parser.add_argument('--unfinished', default=5)
parser.add_argument('--txnsperbatch', default=20)
parser.add_argument('--label', default='onlyround')
args = parser.parse_args()

if not args.exp_dir.endswith("/"):
    args.exp_dir = args.exp_dir + "/"

output_file = args.exp_dir + 'config-saw-intkey.yaml' 

with open(args.template, 'r') as template:
    format_body = template.read() # read the rest of the file as format body

format_body = format_body.replace("{tps}", str(args.tps))
format_body = format_body.replace("{duration}", str(args.duration))
format_body = format_body.replace("{unfinished}", str(args.unfinished))
format_body = format_body.replace("{txnsperbatch}", str(args.txnsperbatch))
format_body = format_body.replace("{label}", args.label)

with open(output_file, 'w') as output:
    output.write(format_body)
