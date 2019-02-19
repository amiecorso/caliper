python3 ~/caliper/experiments/stale_blocks/parse_logs.py
sleep 10
docker-compose -f ~/caliper/experiments/prototest/compose_files/sawtooth-do-nothing.yaml down
docker volume prune -f
python3 ~/caliper/experiments/data_scripts/report_parser.py

