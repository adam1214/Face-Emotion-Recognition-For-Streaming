#!/bin/bash
rm -rf ./*.log
rm -rf ./time_result.txt
#MASTER="140.114.84.204"
MASTER="localhost"
#PORT2=8134
#PORT1=5000
PORT=80

#usage(){
#  echo "Creates a worker and connects it to a master.";
#  echo "If the master address is not given, a master will be created at localhost:80";
#  echo "Usage: $0 -y yaml_file [-m master address] [-p port number]";
#}
#while getopts "h?m:p:y:" opt; do
#    case "$opt" in
#    h|\?)
#        usage
#        exit 0
#        ;;
#    m)  MASTER=$OPTARG
#        ;;
#    p)  PORT=$OPTARG
#        ;;
#    y)  YAML=$OPTARG
#        ;;
#    esac
#done
#yaml file must be specified
#if [ -z "$YAML" ] || [ ! -f "$YAML" ] ; then
#  usage;
#  exit 1;
#fi;

#python3 ./kaldi-gstreamer-server/kaldigstserver/master_server_example.py --port=$PORT2 2>> ./master.log &
python3 ./kaldi-gstreamer-server/kaldigstserver/master_server_example.py --port=$PORT 2>> ./master.log &

#start worker and connect it to the master
#export GST_PLUGIN_PATH=/opt/gst-kaldi-nnet2-online/src/:/opt/kaldi/src/gst-plugin/
for (( i=1; i<=1; i++ ))
do
   log_name="worker$i"
   #python ./kaldi-gstreamer-server/kaldigstserver/worker_example_2.py -u ws://$MASTER:$PORT1/worker/ws/speech 2>> ./$log_name.log &
   python ./kaldi-gstreamer-server/kaldigstserver/worker_example_2.py -u ws://$MASTER:$PORT/worker/ws/speech 2>> ./$log_name.log &
done
