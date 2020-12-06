export FERS_ROOT=$(pwd)

docker run \
-p 8134:80 \
--rm -it --privileged \
--name Fer_server \
-v ${FERS_ROOT}:/media/fer_streaming \
140.114.84.199:4999/fer_streaming_gpu bash