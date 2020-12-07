#!/bin/bash
rm -rf ./*.log
rm -rf ./time_result.txt
MASTER="140.114.84.204"
PORT2=8134
PORT1=5000

python3 ./kaldi-gstreamer-server/kaldigstserver/master_server_example.py --port=$PORT2 2>> ./master.log &

for (( i=1; i<=1; i++ ))
do
   log_name="worker$i"
   python ./kaldi-gstreamer-server/kaldigstserver/worker_example_2.py -u ws://$MASTER:$PORT1/worker/ws/speech 2>> ./$log_name.log &
done
