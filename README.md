# FER_streaming_gpu_ver

> **Engineer Team**  
> last update: 2020.11.01  
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
	1. `git clone https://biicgitlab.ee.nthu.edu.tw/crowpeter/fer_streaming_gpu_ver.git`  

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
        The mp4 path you want to compute.
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

## How to deploy on TWCC 開發型容器 (Edited by Chun Yu Chen)
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
        
## Pressure test on 140.114.84.204 (Localhost) (Edited by Chun Yu Chen)
*    Code explain
        *    allocate_client.sh：How many clients you want to allocate. (for loop)
        *    start.sh：How many workers you want to allocate.(for loop)
        *    avg_sec.py：Estimate average time of all seconds that workers spent.
