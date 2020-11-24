#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 16:06:48 2020

@author: peterwu
"""

import logging
import logging.config
import time
# import os
import argparse
# from subprocess import Popen, PIPE
# from gi.repository import GObject
# import yaml
import json
import sys
import tornado.gen 
import tornado.process
import tornado.ioloop
import tornado.locks
import tornado.websocket
import tensorflow as tf
import common
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import struct
# import cv2
# import pickle
# from fer_moudle import fer_model
import warnings
from threading import Thread

import cv2
# import struct ## new
import pickle
from keras.models import load_model
# import numpy as np
# import tensorflow as tf
import tornado

# from tensorflow.compat.v1 import InteractiveSession
from tensorflow.python.keras.backend import set_session


import threading
from tornado.concurrent import Future
from tornado.platform import asyncio
import asyncio

from tornado.platform.asyncio import AnyThreadEventLoopPolicy
import nest_asyncio

nest_asyncio.apply()
asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

config = tf.ConfigProto()
config.gpu_options.allow_growth = True

sess = tf.Session(config=config)
graph = tf.get_default_graph()
set_session(sess)

warnings.filterwarnings("ignore")
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=5)

CONNECT_TIMEOUT = 5
SILENCE_TIMEOUT = 100
# USE_NNET2 = False
        
class Worker():
    STATE_CREATED = 0
    STATE_CONNECTED = 1
    STATE_INITIALIZED = 2
    STATE_PROCESSING = 3
    STATE_EOS_RECEIVED = 7
    STATE_CANCELLING = 8
    STATE_FINISHED = 100

    def __init__(self, uri):
        global graph
        global sess
        self.uri = uri
        self.partial_transcript = ""
        self.state = self.STATE_CREATED
        self.request_id = "<undefined>"

        self.num_segments = 0
        self.last_partial_result = ""
        # self.post_processor_lock = tornado.locks.Lock()
        # self.processing_condition = tornado.locks.Condition()
        self.num_processing_threads = 0
        
        
        self.img_start_flag = True
        self.img_size = 0
        self.img_data = b''
        self.payload_size = struct.calcsize(">L")        
        self.count = 0
        self.image_in_buf = []
        self.image_out_buf = []
        self.ccount = 0

        self.graph = graph
        # loading face detection model
        self.face_detection = cv2.CascadeClassifier('./model/haarcascade_frontalface_default.xml')
        # loading emo models
        set_session(sess)
        self.emotion_classifier = load_model('./model/fer2013_mini_XCEPTION.102-0.66.hdf5', compile=False)
        # for i in range(3):
        self.emotion_classifier.predict(np.zeros((1,64,64,1)))
            # print(init)
        self.emotion_offsets = (20, 40)
        # getting model output shape for inference
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]
        
        # self.t = threading.Thread(target = self.process_in)
        # self.t.start()
        
    @tornado.gen.coroutine
    def connect_and_run(self):
        self.EOS_flag = False
        logger.info("Opening websocket connection to master server")
        self.ws = yield tornado.websocket.websocket_connect(self.uri, ping_interval=10)
        logger.info("Opened websocket connection to server")
        self.state = self.STATE_CONNECTED
        self.last_partial_result = ""
        self.last_decoder_message = time.time()
        while True:
            # tornado.ioloop.IOLoop.add_callback(self.detect_and_send())
            msg = yield self.ws.read_message()
            self.received_message(msg)
            # print(len(self.image_in_buf))
            if msg is None:
                # print(0)
                print('msg is none')
                self.closed()
                break
        logger.info("Finished decoding run")
        
    # @tornado.gen.coroutine
    def process_in(self):
        global sess
        global graph
        # while True:
        while self.state in [self.STATE_EOS_RECEIVED, self.STATE_CONNECTED, self.STATE_INITIALIZED, self.STATE_PROCESSING]:
            if self.image_in_buf:
                if self.image_in_buf[0] == 'EOS':
                    # self.image_out_buf.append('EOS')
                    del self.image_in_buf[0]
                    self.feedback_end_to_master()
                    # self.finish_request()
                    continue
                # try:
                    # self._increment_num_processing(1)
                #1
                else:
                    gray_img = self.img_pre_processing(self.image_in_buf[0])
                    faces = self.detect_faces(gray_img)
                    # print(faces)
                    if len(faces): #face detected!
                        for face in faces:
                            # print(face)
                            gray_face = self.face_pre_processing(gray_img, face)
                            if gray_face is None:
                                continue
                            with graph.as_default():
                                set_session(sess)
                                # print(gray_face.shape)
                                emo = self.emotion_classifier.predict(gray_face)
                            self.last_decoder_message = time.time()
                            event = dict(status=common.STATUS_SUCCESS,
                                          result=dict(hypotheses=[dict(transcript='return result',\
                                                                       emo=emo.tolist(),\
                                                                       face=face.tolist())],
                                                                       final=False,count=self.ccount))
                            self.image_out_buf.append(event)
                            # try:
                            #     self.ws.write_message(json.dumps(event))
                            #     del event
                            # except:
                            #     e = sys.exc_info()[1]
                            #     print('ERROR_face_respond')
                            #     print(e)
                            #     logger.warning("Failed to send event to master: %s" % e)
                                
                    else: #no face detected!
                        event = dict(status=common.STATUS_SUCCESS,
                                      result=dict(hypotheses=[dict(transcript='return result',\
                                                                   emo=[],\
                                                                   face=[])],
                                                                   final=False,count=self.ccount))
                        self.image_out_buf.append(event)
                        # try:
                        #     self.ws.write_message(json.dumps(event))
                        #     del event
                        # except:
                        #     e = sys.exc_info()[1]
                        #     print('ERROR_noface_respond')
                        #     print(e)
                        #     logger.warning("Failed to send event to master: %s" % e)
                                
                    del self.image_in_buf[0]
                    self.ccount+=1
                time.sleep(0.001)
                    # self.last_decoder_message = time.time()
            else:
                pass
    
    def run_send(self):
        if self.image_out_buf:
            event = self.image_out_buf[0]
            try:
                self.ws.write_message(json.dumps(event))
                del self.image_out_buf[0]
            except:
                e = sys.exc_info()[1]
                print('ERROR_face_respond')
                print(e)
                logger.warning("Failed to send event to master: %s" % e)
        else:
            pass

    def guard_timeout(self):
        global SILENCE_TIMEOUT
        while self.state in [self.STATE_EOS_RECEIVED, self.STATE_CONNECTED, self.STATE_INITIALIZED, self.STATE_PROCESSING]:
            if time.time() - self.last_decoder_message > SILENCE_TIMEOUT:
                logger.warning("%s: More than %d seconds from last decoder hypothesis update, cancelling" % (self.request_id, SILENCE_TIMEOUT))
                self.finish_request()
                event = dict(status=common.STATUS_NO_SPEECH)
                try:
                    self.ws.write_message(json.dumps(event))
                except:
                    logger.warning("%s: Failed to send error event to master" % (self.request_id))
                self.ws.on_close()
                self.ws.close()
                return
            logger.debug("%s: Checking that decoder hasn't been silent for more than %d seconds" % (self.request_id, SILENCE_TIMEOUT))
            time.sleep(1)

    def received_message(self, m):
        logger.debug("%s: Got message from server of type %s" % (self.request_id, str(type(m))))
        if self.state == self.__class__.STATE_CONNECTED:
            props = json.loads(m)
            # content_type = props['content_type']
            self.request_id = props['id']
            self.num_segments = 0
            # self.decoder_pipeline.init_request(self.request_id, content_type)
            self.last_decoder_message = time.time()
            
            tornado.ioloop.IOLoop.instance().run_in_executor(executor, self.process_in)
            
            self.image_in_buf = []
            self.image_out_buf = []
            
            logger.info("%s: Started timeout guard" % self.request_id)
            logger.info("%s: Initialized request" % self.request_id)
            self.state = self.STATE_INITIALIZED
        elif m == "EOS":
            
            if self.state != self.STATE_CANCELLING and self.state != self.STATE_EOS_RECEIVED and self.state != self.STATE_FINISHED:
                self.state = self.STATE_PROCESSING
                self.image_in_buf.append(m)
                
            else:
                logger.info("%s: Ignoring EOS, worker already in state %d" % (self.request_id, self.state))
                
        else:
            if self.state != self.STATE_CANCELLING and self.state != self.STATE_EOS_RECEIVED and self.state != self.STATE_FINISHED:
                self.run_send()
                if isinstance(m, bytes):
                    rev_m = m
                    if self.img_start_flag:
                        
                        self.img_size = struct.unpack(">L", rev_m[:self.payload_size])[0]
                        self.img_data += rev_m[self.payload_size:]
                        self.img_start_flag = False
                        
                    else:
                        self.img_data += rev_m
                        if len(self.img_data) == self.img_size:
                            self.count+=1
                            self.image_in_buf.append(self.img_data)
                            # initial
                            del self.img_data
                            self.img_start_flag = True
                            self.img_size = 0
                            self.img_data = b''
                            
                        elif len(self.img_data) > self.img_size:
                            print('ERROR_size_mismatch')
                        
                    self.state = self.STATE_PROCESSING
                    
                elif isinstance(m, str):
                    props = json.loads(str(m))
                    print(props)
                    
            else:
                logger.info("%s: Ignoring data, worker already in state %d" % (self.request_id, self.state))

    def finish_request(self):
        if self.state == self.STATE_EOS_RECEIVED:
            # connection closed when we are not doing anything
            self.state = self.STATE_FINISHED
            return
        if self.state == self.STATE_CONNECTED:
            # connection closed when we are not doing anything
            self.state = self.STATE_FINISHED
            return
        if self.state == self.STATE_INITIALIZED:
            # connection closed when request initialized but with no data sent
            self.state = self.STATE_FINISHED
            return
        if self.state != self.STATE_FINISHED:
            logger.info("%s: Master disconnected before decoder reached EOS?" % self.request_id)
            self.state = self.STATE_CANCELLING
            counter = 0
            while self.state == self.STATE_CANCELLING:
                counter += 1
                if counter > 30:
                    # lost hope that the decoder will ever finish, likely it has hung
                    # FIXME: this might introduce new bugs
                    logger.info("%s: Giving up waiting after %d tries" % (self.request_id, counter))
                    self.state = self.STATE_FINISHED
                else:
                    logger.info("%s: Waiting for EOS from decoder" % self.request_id)
                    time.sleep(1)
            logger.info("%s: Finished waiting for EOS" % self.request_id)


    def closed(self):
        logger.debug("%s: Websocket closed() called" % self.request_id)
        self.finish_request()
        logger.debug("%s: Websocket closed() finished" % self.request_id)

  
    @tornado.gen.coroutine
    def feedback_end_to_master(self):     
        self.state = self.STATE_EOS_RECEIVED
        
        self.last_decoder_message = time.time()
        event = dict(status=common.STATUS_SUCCESS,
                     adaptation_state=dict(id=self.request_id,
                                           segment=self.num_segments,
                                           result=dict(hypotheses=[dict(transcript='received EOS, stop')],final=True),
                                           time=time.strftime("%Y-%m-%dT%H:%M:%S")))
        try:
            self.ws.write_message(json.dumps(event))
            del event
        except:
            logger.warning("%s: Failed to send error event to master" % (self.request_id))
        self.state = self.STATE_FINISHED
        self.ws.close()
        
    def img_pre_processing(self, rev_message):
        frame = pickle.loads(rev_message, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def detect_faces(self, gray_image_array):
        return self.face_detection.detectMultiScale(gray_image_array, 1.3, 5)
    
    def face_pre_processing(self, gray_image_array ,face_coordinate):
        x1, x2, y1, y2 = self.apply_offsets(face_coordinate, self.emotion_offsets)
        gray_face = gray_image_array[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (self.emotion_target_size))
        except:
            return None
        gray_face = self.preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        return gray_face
    
    def emo_predict(self, gray_face):
        global sess
        global graph
        global emotion_classifier
        with graph.as_default():
            emo = emotion_classifier.predict(gray_face)
        return emo
    
    def apply_offsets(self, face_coordinates, offsets):
        x, y, width, height = face_coordinates
        x_off, y_off = offsets
        return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)
    
    def preprocess_input(self, x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x

@tornado.gen.coroutine
def main_loop(uri, full_post_processor=None):
    while True:
        worker = Worker(uri)
        try:            
            yield worker.connect_and_run()
        except Exception:
            logger.error("Couldn't connect to server, waiting for %d seconds", CONNECT_TIMEOUT)
            yield tornado.gen.sleep(CONNECT_TIMEOUT)
        # fixes a race condition
        yield tornado.gen.sleep(0.1)
        

def main():
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")
    logging.debug('Starting up worker')
    parser = argparse.ArgumentParser(description='Worker for kaldigstserver')
    #parser.add_argument('-u', '--uri', default="ws://localhost:8888/worker/ws/speech", dest="uri", help="Server<-->worker websocket URI")
    parser.add_argument('-u', '--uri', default="ws://140.114.84.204:8134/worker/ws/speech", dest="uri", help="Server<-->worker websocket URI")
    parser.add_argument('-f', '--fork', default=1, dest="fork", type=int)

    args = parser.parse_args()

    if args.fork > 1:
        logging.info("Forking into %d processes" % args.fork)
        tornado.process.fork_processes(args.fork)

    # fork off the post-processors before we load the model into memory
    tornado.process.Subprocess.initialize()
    tornado.ioloop.IOLoop.current().add_callback(main_loop, args.uri)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
