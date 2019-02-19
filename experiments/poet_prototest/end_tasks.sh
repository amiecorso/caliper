python3 ~/caliper/experiments/stale_blocks/parse_logs.py --n 5 --dest ~/caliper/experiments/poet_prototest/results/ --rest_url http://sawtooth-rest-api-default-0:8008
sleep 15
docker-compose -f ~/caliper/experiments/poet_prototest/compose_files/poet-do-nothing.yaml down
docker volume prune -f
python3 ~/caliper/experiments/data_scripts/report_parser.py --reportpath ~/caliper/experiments/poet_prototest/ --dest ~/caliper/experiments/poet_prototest/results/ --n 5


