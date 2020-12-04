sudo docker run -it --rm --name Fer_client --link Fer_server fer_client \
/bin/bash -c "python client_example.py -u ws://Fer_server:80/client/ws/speech -v False -info False ./Test.mp4"