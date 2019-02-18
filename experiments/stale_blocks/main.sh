python3 start_network.py &
sleep 20 
python3 deliver_workload.py
sleep 20
python3 parse_logs.py
sleep 5
python3 stop_network.py
docker volume prune -f # seems to be necessary after running any network with PoET enabled
