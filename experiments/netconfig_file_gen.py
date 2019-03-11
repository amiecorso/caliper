# netconfig_file_gen.py

import argparse
import os

parser = argparse.ArgumentParser(description="Generate network configuration file from specified template, pointing to composefile/network of specified size.")
parser.add_argument('--n', default=1, type=int, help="The network size for this Caliper run")
parser.add_argument('--template', default='/Users/amiecorso/caliper/experiments/templates/net_config_template.json', help="The template file from which to create network config file.")
parser.add_argument('--dest', default='/Users/amiecorso/caliper/experiments/test/', help="Destination directory for output file")
parser.add_argument('--exp_dir', default='/Users/amiecorso/caliper/experiments/poet_prototest', help="The directory of this experiment")
parser.add_argument('--TPfamily', default='donothing', help="The name of the transaction processor family for this workload")
parser.add_argument('--bb_file', default='DoNothingBatchBuilder.js', help="The name of the .js BatchBuilder file for this transaction family, located in src/adapters/sawtooth/Application/")
args = parser.parse_args()

if not args.dest.endswith("/"):
    args.dest = args.dest + "/"

if not os.path.exists(args.dest):
    os.mkdir(args.dest)

base_filename = args.template.split('/')[-1].replace("_template", "") # get rid of 'template' tag
output_file = str(args.n) + "_" + base_filename


with open(args.template, 'r') as template:
    format_body = template.read() # read the rest of the file as format body

# assign rest-api url array
restapi_array = "["
for i in range(args.n):
    next_port = str(8008 + i)
    next_url = "http://127.0.0.1:" + next_port
    restapi_array += "\"" + next_url + "\", "
restapi_array = restapi_array.rstrip(", ") + "]"

format_body = format_body.replace("{n}", str(args.n))
format_body = format_body.replace("{exp_dir}", args.exp_dir)
format_body = format_body.replace("{TPfamily}", args.TPfamily)
format_body = format_body.replace("{batchbuilder_file}", args.bb_file)
format_body = format_body.replace("{restapi_urls}", restapi_array)

with open(args.dest + output_file, 'w') as output:
    output.write(format_body)
