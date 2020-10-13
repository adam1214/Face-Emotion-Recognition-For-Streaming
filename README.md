# FER_streaming_gpu_ver

> **Engineer Team**  
> last update: 2020.10.13  
> 
> @ author: Peter Wu  
> @ email: crowpeter27@gmail.com  
> @ mattermost: crowpeter27  


## Requirement
* **Image**   
	1. Install docker, opencv, keras, tornado in your device  
	2. Use your account login to gitlab `docker login biicgitlab.ee.nthu.edu.tw:5050`  
	3. Download the image `sudo docker pull 140.114.84.199:4999/fer_streaming_gpu`  
* **Code structure**  
	1. `git clone https://biicgitlab.ee.nthu.edu.tw/crowpeter/fer_streaming_gpu`  

## Run docker and server
* After download the image and code, please follow the step as below:
    1. `cd <your_path>`
    2.  Start container: 

        `sudo docker run --gpus all -it --privileged -ti -p 8080:80 -v <your_path>:/media/fer_streaming 140.114.84.199:4999/fer_streaming_gpu bash`
    3.  Check whether the `start.sh` and `stop.sh` in the folder `/media/ferstreaming` of your container.
    4.  Start server: `./start.sh`
    5.  Run client in your local:
    
        `python kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://localhost:8080/client/ws/speech -v False -info False ./example_wav/Test.mp4`

## Main code explain
* **master_server_example.py**

    The master for controling communication between worker and client

* **worker_example.py**

    The main block process video and feedback the result, you can carry out multiple worker to process multiple client request.

* **client_example.py**

    Sending a video to master to do FER. The parameter explain as below:
    1. -u [default:ws://localhost:8080/client/ws/speech]
        The url you wnat to connect.
    2. -video [default:True]
        Show the result on your screen or not.
    3. -info [default:True]
        Save the result in fer_result
    4. audiofile [default: ./example_wav/Test.mp4]
        The mo4 path you want to compute.
    (recommand)

## Output Format
    There are `.csv` files in the `kaldi-gstreamer-server/fer_result` folder. And each colume in the `.csv` file is:
    * time
    * frame
    * face_x
    * face_y
    * face_w
    * face_h
    * emotion
