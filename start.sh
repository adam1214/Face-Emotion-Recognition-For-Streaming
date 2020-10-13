#!/bin/bash
rm -rf ./*.log
MASTER="localhost"
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


if [ "$MASTER" == "localhost" ] ; then
  # start a local master
  python3 ./kaldi-gstreamer-server/kaldigstserver/master_server_example.py --port=$PORT 2>> ./master.log &
  #python3 ./kaldi-gstreamer-server/kaldigstserver/master_server_example.py >> ./master.log &
fi

#start worker and connect it to the master
#export GST_PLUGIN_PATH=/opt/gst-kaldi-nnet2-online/src/:/opt/kaldi/src/gst-plugin/

python ./kaldi-gstreamer-server/kaldigstserver/worker_example.py -u ws://$MASTER:$PORT/worker/ws/speech 2>> ./worker1.log &
#python3 ./kaldi-gstreamer-server/kaldigstserver/worker_example.py -u ws://$MASTER:$PORT/worker/ws/speech 2>> ./worker2.log &
