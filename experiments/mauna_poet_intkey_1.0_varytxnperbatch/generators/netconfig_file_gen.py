# netconfig_file_gen.py

import argparse
import os

parser = argparse.ArgumentParser(description="Generate network configuration file from specified template, pointing to composefile/network of specified size.")
parser.add_argument('--n', default=1, type=int, help="The network size for this Caliper run")
parser.add_argument('--template', default='../templates/net_config_template.json', help="The template file from which to create network config file.")
parser.add_argument('--dest', default='/Users/amiecorso/caliper/experiments/test/', help="Destination directory for output file")
parser.add_argument('--exp_dir', default='/Users/amiecorso/caliper/experiments/poet_prototest', help="The directory of this experiment")
parser.add_argument('--TPfamily', default='donothing', help="The name of the transaction processor family for this workload")
parser.add_argument('--bb_file', default='DoNothingBatchBuilder.js', help="The name of the .js BatchBuilder file for this transaction family, located in src/adapters/sawtooth/Application/")
parser.add_argument('--run_num', help="The repeat we're on, for performing identical runs of same workload")
parser.add_argument('--leave_up',default="False", help="Leave the Docker network running after workload delivery?")
parser.add_argument('--tps')
parser.add_argument('--interval')
parser.add_argument('--remoteip')
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
    next_url = "http://" + args.remoteip + ":" + next_port
    restapi_array += "\"" + next_url + "\", "
restapi_array = restapi_array.rstrip(", ") + "]"
validator_url = "\"tcp://" + args.remoteip + ":8800\""

format_body = format_body.replace("{n}", str(args.n))
format_body = format_body.replace("{exp_dir}", args.exp_dir)
format_body = format_body.replace("{run_num}", args.run_num)
format_body = format_body.replace("{leave_up}", str(args.leave_up))
format_body = format_body.replace("{TPfamily}", args.TPfamily)
format_body = format_body.replace("{batchbuilder_file}", args.bb_file)
format_body = format_body.replace("{restapi_urls}", restapi_array)
format_body = format_body.replace("{validator_url}", validator_url)
format_body = format_body.replace("{tps}", str(args.tps))
format_body = format_body.replace("{interval}", str(args.interval))
format_body = format_body.replace("{remoteip}", str(args.remoteip))


with open(args.dest + output_file, 'w') as output:
    output.write(format_body)
