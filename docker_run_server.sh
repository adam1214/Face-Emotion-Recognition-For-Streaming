export FERS_ROOT=$(pwd)

docker run \
-p 5000:8134 \
--rm -it --privileged \
-v ${FERS_ROOT}:/media/fer_streaming \
140.114.84.199:4999/fer_streaming_gpu bash
