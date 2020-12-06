export FERS_ROOT=$(pwd)

if [ $# -eq 0 ]
then
    echo "NO argument supplied (real time)"
    docker run  --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY \
    -v ${FERS_ROOT}:/media/fer_streaming \
    -v /dev/video0:/dev/video0 -it --rm --name Fer_client \
    --link Fer_server \
    fer_client \
    /bin/bash -c "python ./kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://Fer_server:80/client/ws/speech -v True -info False -1"

else
    echo "Arguments supplied"
    docker run  --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY \
    -v ${FERS_ROOT}:/media/fer_streaming \
    -v /dev/video0:/dev/video0 -it --rm --name Fer_client \
    --link Fer_server \
    fer_client \
    /bin/bash -c "python ./kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://Fer_server:80/client/ws/speech -v True -info False $1"
fi
