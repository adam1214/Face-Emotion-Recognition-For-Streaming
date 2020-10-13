import argparse
#from ws4py.client.threadedclient import WebSocketClient
import time
import threading
import sys
import urllib
import queue
import json
import time
import os
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

import cv2
import csv
import pickle
import struct
import codecs
import numpy as np

def rate_limited(maxPerSecond):
    min_interval = 1.0 / float(maxPerSecond)
    def decorate(func):
        last_time_called = [0.0]
        def rate_limited_function(*args,**kargs):
            elapsed = time.clock() - last_time_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                yield gen.sleep(left_to_wait)
            ret = func(*args,**kargs)
            last_time_called[0] = time.clock()
            return ret
        return rate_limited_function
    return decorate

executor = ThreadPoolExecutor(max_workers=5)

class MyClient():

    def __init__(self, audiofile, url,
                 save_adaptation_state_filename=None, send_adaptation_state_filename=None,
                 show_video=True, save_info=True):
        self.url = url
        self.show_video = show_video
        self.final_hyps = []
        self.global_img_box = []
        # self.audiofile = audiofile
        if audiofile == '-1':
            self.audiofile = cv2.VideoCapture(int(audiofile))
        else:
            self.audiofile = cv2.VideoCapture(audiofile)
        
        self.fps_float = self.audiofile.get(cv2.CAP_PROP_FPS)
        self.fps = round(self.fps_float )

        self.save_info = save_info
        
        if self.save_info:
            info_name = ['time', 'frame', 'face_x', 'face_y', 'face_w', 'face_h', 'emotion']
            v_name = audiofile.split('/')[-1]
            self.csv_info = codecs.open('./fer_result/'+v_name+'.csv', 'w', encoding="utf_8_sig")
            self.csv_writer = csv.writer(self.csv_info)
            self.csv_writer.writerow(info_name)

        # self.byterate = byterate
        self.final_hyp_queue = queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.server_end_flag=False
        self.ioloop = IOLoop.current()
        self.run()
        self.ioloop.start()
        

            
    @gen.coroutine
    def run(self):
        
        c=0
        connect_flag = True
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90] 
        
        self.ws = yield websocket_connect(self.url, on_message_callback=self.received_message)
        if self.send_adaptation_state_filename is not None:
            print("Sending adaptation state from " + self.send_adaptation_state_filename)
            try:
                adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                self.ws.write_message(json.dumps(dict(adaptation_state=adaptation_state_props)))
            except:
                e = sys.exc_info()[0]
                print("Failed to send adaptation state: " + e)
        
        while connect_flag:
            ret, frame = self.audiofile.read()

            if not ret:
                connect_flag = False
                break
            
            self.global_img_box.append(frame)
            
            result, frame2 = cv2.imencode('.jpg', frame, encode_param)
            data = pickle.dumps(frame2)
            size = len(data)
            # print(size)
            data = struct.pack(">L", size) + data
            # print(len(data))
            for i in range(0,len(data),60000):
                yield self.send_data(data[i:i+60000])
                
        self.ws.write_message("EOS")
    
    @gen.coroutine
    @rate_limited(100)
    def send_data(self, data):
        self.ws.write_message(data, binary=True)

    def received_message(self, m):
        if m is None:
            #print("Websocket closed() called")
            self.final_hyp_queue.put(" ".join(self.final_hyps))
            self.ioloop.stop()
            return
        
        # print(str(m) + "\n")
        response = json.loads(str(m))
        
        if response['status'] == 0:
            # print(response)
            if 'result' in response:
                emo_prob = response['result']['hypotheses'][0]['emo']
                face_coor =  response['result']['hypotheses'][0]['face']
                frame_idx = response['result']['count']
                print(frame_idx, emo_prob, face_coor)
                # print(self.global_img_box[frame_idx])
                if face_coor:
                    emo_txt, color = self.make_color_and_test(emo_prob)
                    
                    if self.save_info:
                        op_info_list = [round(frame_idx/self.fps_float, 3), frame_idx,
                                        face_coor[0], face_coor[1],
                                        face_coor[2], face_coor[3], emo_txt]
                        for i in range(len(op_info_list)):
                            op_info_list[i] = str(op_info_list[i])
                        self.csv_writer.writerow(op_info_list)

                    if self.show_video:
                        self.draw_bounding_box(face_coor, self.global_img_box[frame_idx], color=color)
                        self.draw_text(face_coor, self.global_img_box[frame_idx], emo_txt,
                                       color, 0, -45, 1, 1)
                if self.show_video:      
                    cv2.imshow('respond', np.array(self.global_img_box[frame_idx], dtype = np.uint8 ))
                    cv2.waitKey(1)
                
                
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    print("Saving adaptation state to " + self.save_adaptation_state_filename)
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
                # print('HIHI')
                if self.save_info:
                    self.csv_info.close()
                self.ioloop.stop()
        else:
            print("Received error from server (status %d)" % response['status'])
            if 'message' in response:
                print("Error message:" + response['message'])


    def get_full_hyp(self, timeout=10):
        return self.final_hyp_queue.get(timeout)

    # def closed(self, code, reason=None):
    #     print("Websocket closed() called")
    #     self.final_hyp_queue.put(" ".join(self.final_hyps))
    def draw_text(self, coordinates, image_array, text, color, x_offset=0, y_offset=0,
                                                    font_scale=2, thickness=2):
        x, y = coordinates[:2]
        cv2.putText(image_array, text, (x + x_offset, y + y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, color, thickness, cv2.LINE_AA)    
        
    def draw_bounding_box(self, face_coordinates, image_array, color):
        x, y, w, h = face_coordinates[0], face_coordinates[1], face_coordinates[2], face_coordinates[3]
        cv2.rectangle(image_array, (x, y), (x + w, y + h), color, 2)
    
    def make_color_and_test(self, emo_pred):
        emotion_labels = {0: 'angry',1: 'disgust',2: 'fear',3: 'happy',4: 'sad',5: 'surprise',6: 'neutral'}
        emotion_probability = np.max(emo_pred)
        emotion_label_arg = np.argmax(emo_pred)
        emotion_text = emotion_labels[emotion_label_arg]

        if emotion_text == 'angry':
            color = emotion_probability * np.asarray((255, 0, 0))
        elif emotion_text == 'sad':
            color = emotion_probability * np.asarray((0, 0, 255))
        elif emotion_text == 'happy':
            color = emotion_probability * np.asarray((255, 255, 0))
        elif emotion_text == 'surprise':
            color = emotion_probability * np.asarray((0, 255, 255))
        else:
            color = emotion_probability * np.asarray((0, 255, 0))

        color = color.astype(int)
        color = color.tolist()
        return emotion_text, color
    
def main():

    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri", help="Server websocket URI")
    parser.add_argument('-video', default='True', help="show video on screen")
    parser.add_argument('-info', default='True', help="save info to fer_result")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='', help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    # parser.add_argument('audiofile', help="Audio file to be sent to the server", type=argparse.FileType('rb'))
    parser.add_argument('audiofile', help="Audio file to be sent to the server")
    args = parser.parse_args()

    content_type = args.content_type
    
    v = False
    if args.video == 'True':
        v = True
    elif args.video == 'False':
        v = False
    else:
        v = False
    info = False
    if args.info == 'True':
        info = True
    elif args.info == 'False':
        info = False
    else:
        info = False
    ws = MyClient(args.audiofile, args.uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])),
                  save_adaptation_state_filename=args.save_adaptation_state, send_adaptation_state_filename=args.send_adaptation_state,
                  show_video=v, save_info=info)
    # result = ws.get_full_hyp()
    # print(result)
    

if __name__ == "__main__":
    t = time.time()
    main()
    print(time.time()-t)