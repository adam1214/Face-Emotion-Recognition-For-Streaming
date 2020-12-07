export FERS_ROOT=$(pwd)

if [ $# -eq 0 ]
then
    echo "NO argument supplied (real time)"
    docker run  --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY \
    -v ${FERS_ROOT}:/media/fer_streaming \
    -v /dev/video0:/dev/video0 -it --rm --name Fer_client \
    140.114.84.199:4999/fers_client \
    /bin/bash -c "python ./kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://140.114.84.204:5000/client/ws/speech -v True -info False -1"

else
    echo "Arguments supplied"
    docker run  --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY \
    -v ${FERS_ROOT}:/media/fer_streaming \
    -v /dev/video0:/dev/video0 -it --rm --name Fer_client \
    140.114.84.199:4999/fers_client \
    /bin/bash -c "python ./kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://140.114.84.204:5000/client/ws/speech -v True -info False $1"
fi
