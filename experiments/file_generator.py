import argparse

parser = argparse.ArgumentParser(description="Generate files for creating Sawtooth network of specified size, from specified template.")
parser.add_argument('--n', default=1, type=int, help="The number of validators to create")
parser.add_argument('--template', default='/Users/amiecorso/caliper/experiments/templates/sawtooth-poet.yaml', help="The template file from which to create validators")
args = parser.parse_args()

with open(args.template, 'r') as template:
    template.readline() # move past header
    lines = template.readlines()

header_lines = []
for line in lines:
    if "end header" in line:
        break
    header_lines.append(line)


print("HEADER: ", header_lines)
