# compose_file_gen.py

import argparse
import os

parser = argparse.ArgumentParser(description="Generate files for creating Sawtooth network of specified size, from specified template.")
parser.add_argument('--n', default=1, type=int, help="The number of validators to create")
parser.add_argument('--template', default='/Users/amiecorso/caliper/experiments/templates/sawtooth-poet.yaml', help="The template file from which to create validators")
parser.add_argument('--dest', default='/Users/amiecorso/caliper/experiments/test/', help="Destination directory for output file")
args = parser.parse_args()

if not args.dest.endswith("/"):
    args.dest = args.dest + "/"

if not os.path.exists(args.dest):
    os.mkdir(args.dest)

base_filename = args.template.split("/")[-1].split("_")[0] 
if not base_filename.endswith(".yaml"):
    base_filename = base_filename + ".yaml"

output_file = str(args.n) + "_" + base_filename

header_and_genesis = []

with open(args.template, 'r') as template:
    template.readline() # move past header
    line = template.readline()
    while "end genesis" not in line:
        header_and_genesis.append(line)        
        line = template.readline()

    format_body = template.read() # read the rest of the file as format body


with open(args.dest + output_file, 'w') as output:
    output.write("# " + output_file + "\n")
    output.writelines(header_and_genesis)
    for i in range(1, args.n):
        next_validator = format_body.replace("{}", str(i))
        output.write(next_validator)

