#!/bin/bash
for (( i=1; i<=1; i++ ))
do
   python kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://localhost:8134/client/ws/speech -v False -info False ./example_wav/Test.mp4 &

done
