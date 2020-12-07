#!/bin/bash
rm -rf ./*.log
rm -rf ./time_result.txt
MASTER="localhost"
PORT=80

python3 ./kaldi-gstreamer-server/kaldigstserver/master_server_example.py --port=$PORT 2>> ./master.log &

for (( i=1; i<=1; i++ ))
do
   log_name="worker$i"
   python ./kaldi-gstreamer-server/kaldigstserver/worker_example_2.py -u ws://$MASTER:$PORT/worker/ws/speech 2>> ./$log_name.log &
done
