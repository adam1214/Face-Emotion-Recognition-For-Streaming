# FER_streaming_gpu_ver

> **Engineer Team**  
> last update: 2020.12.07  
> 
> @ author: Peter Wu & Chun-Yu Chen  
> @ email: crowpeter27@gmail.com & adam@gapp.nthu.edu.tw  
> @ mattermost: crowpeter27 & chen-chun-yu 


## Requirement
* **Image**   
	1. Install docker, opencv, keras, tornado in your device  
	2. Use your account login to gitlab `docker login biicgitlab.ee.nthu.edu.tw:5050`  
	3. Download the server image `sudo docker pull 140.114.84.199:4999/fer_streaming_gpu`  
	4. Download the client image `sudo docker pull biicgitlab.ee.nthu.edu.tw:5050/prod/engineer/fers_client`  
* **Code structure**  
	1. `git clone https://biicgitlab.ee.nthu.edu.tw/prod/engineer/fer_streaming_gpu_ver.git`  

## Run server container
* After download the image and code, please follow the step as below:
    1.  Start container: 
        *    If localhost: `sudo bash docker_run_server_localhost.sh`
        *    If no localhost: `sudo bash docker_run_server.sh`
    3.  Check whether the `start.sh` and `start_localhost.sh` and `stop.sh` in the folder `/media/ferstreaming` of your container.
    4.  Start server:
        *    If localhost: `bash start_localhost.sh`
        *    If no localhost: `bash start.sh`

## Run client container
* After download the image and code, please follow the step as below:
    1. `cd <your_path>`
    2. Start container: 
        *    no argument (real time):
                *    If localhost: `sudo bash docker_run_client_localhost.sh`
                *    If no localhost(connect to 140.114.84.204:5000): `sudo bash docker_run_client.sh`
        *    with argument (specific `.mp4` file):
                *    If localhost: `sudo bash docker_run_client_localhost.sh example_wav/Test.mp4`
                *    If no localhost(connect to 140.114.84.204:5000): `sudo bash docker_run_client.sh example_wav/Test.mp4`
## Main code explain
* **master_server_example.py**

    The master for controling communication between worker and client

* **worker_example.py**

    The main block process video and feedback the result, you can carry out multiple worker to process multiple client request.

* **client_example.py**

    Sending a video to master to do FER. The parameter explain as below:
    1. -u
        The url you want to connect.
    2. -video
        Show the result on your screen or not.
    3. -info
        Save the result in fer_result
    4. audiofile
        The mp4 path you want to compute.

## Output Format
    There are `.csv` files in the `kaldi-gstreamer-server/fer_result` folder. And each colume in the `.csv` file is:
        * time
        * frame
        * face_x
        * face_y
        * face_w
        * face_h
        * emotion

## Master-Worker pressure test on 140.114.84.204 (Edited by Chun Yu Chen)
*    Code explain
        *    allocate_client.sh：How many clients you want to allocate. (for loop)
        *    start.sh：How many workers you want to allocate. (for loop)
        *    avg_sec.py：Estimate average time of all seconds that workers spent.

*    Pressure test result
        *   localhost (ubuntu) (5 sec, 1080p resize to 720p)
            *    1 worker：8.64s
            *    2 worker：8.19s
            *    3 worker：8.09s
            *    4 worker：8.29s
            *    5 worker：8.72s
            *    10 worker：14.37s
            *    15 worker：21.58s
        *   non-localhost by vpn (ubuntu Virtual Machine) (5 sec, 1080p resize to 720p)
            *   1 worker：11.63s
            *   2 worker：26.21s
            *   3 worker：40.19s
            *   4 worker：53.92s
            *   5 worker：65.15s (Maximum difference:10s)
            *   10 worker：146.47s (Maximum difference:20s)
            *   15 worker：237.43s (Maximum difference:47s)
        *   non-localhost by 713 PC (ubuntu) (5 sec, 1080p resize to 720p)
            *   1 worker：8.31
            *   2 worker：8.97
            *   3 worker：9.58
            *   4 worker：10.19
            *   5 worker：10.55
            *   10 worker：16.44
            *   15 worker：23.97
        *   non-localhost by 713 PC (ubuntu) (5 sec, 1080p resize to 480p)
            *   1 worker：6.68
            *   2 worker：6.80
            *   3 worker：6.78
            *   4 worker：6.93
            *   5 worker：7.44
            *   10 worker：11.21
            *   15 worker：15.12

## How to deploy on TWCC 開發型容器
*    Construct a container

    1. Container image type：tensorflow-18.10-py3-v1
    2. Choose the basic settings you want (ex: GPU, CPU, memory...)
*    Use SSH connection software like MobaXterm. This SSH connection software must support X11 forwarding technology. [Usage](https://www.twcc.ai/doc?page=container&euqinu=true#%E4%BD%BF%E7%94%A8-SSH-%E7%99%BB%E5%85%A5%E9%80%A3%E7%B7%9A)

        1. git clone https://biicgitlab.ee.nthu.edu.tw/crowpeter/fer_streaming_gpu_ver.git
        2. According to /docker/Dockerfile, please use `apt-get update` and `pip --no-cache-dir install` to build enviroment. In terms of installing OpenCV, just type `pip install opencv-contrib-python` instead of following Dockerfile. (TWCC Container hasn't support Docker yet.)
        3. Follow [this](https://www.evernote.com/shard/s102/client/snv?noteGuid=a316760b-4496-4a65-87bb-9cdc7c785988&noteKey=24f512e80c098103&sn=https%3A%2F%2Fwww.evernote.com%2Fshard%2Fs102%2Fsh%2Fa316760b-4496-4a65-87bb-9cdc7c785988%2F24f512e80c098103&title=%255Bsop%255D%2Btwcc%2Bx11%2B%25E5%259C%2596%25E5%25BD%25A2%25E4%25BB%258B%25E9%259D%25A2%25E6%2594%25AF%25E6%258F%25B4&fbclid=IwAR3igPMHlsfPRl1rZFM5lfkrlCin9cRjgBYJhSnvG6hRhozKGZW7HDmXjP8) to support X11 forwarding technology.
        4. Type `firefox` on terminal to open the browser. And follow [this](https://blog.csdn.net/fengxinzioo/article/details/101679140) to install CUDNN 7.6.0.
        5. After building enviroment, you can construct "複本" (similar as        snapshot) to store environment state. Once you want to construct another container to deploy this project, you can use this "複本" in Custom Image. [Usage](https://man.twcc.ai/@twccdocs/SJlZnSOaN?type=view#%E9%96%8B%E7%99%BC%E5%9E%8B%E5%AE%B9%E5%99%A8%E8%A4%87%E6%9C%AC)

*    Follow [this](https://man.twcc.ai/@twccdocs/SJlZnSOaN?type=view#%E8%A8%AD%E5%AE%9A%E5%AE%B9%E5%99%A8%E6%9C%8D%E5%8B%99%E5%9F%A0) to set service port on `5000`.
*    In repository:
        *    Check line 437 in `kaldi-gstreamer-server/kaldigstserver/worker_example.py`(`parser.add_argument('-u'...`): localhost must be `5000`.
        *    Check line 4 in `start.sh`: `PORT=5000`.
*    Start server: `./start.sh` (check master.log and worker1.log)
*    Run client in your local:
    
        `python kaldi-gstreamer-server/kaldigstserver/client_example.py -u ws://localhost:5000/client/ws/speech -v False -info False ./example_wav/Test.mp4`