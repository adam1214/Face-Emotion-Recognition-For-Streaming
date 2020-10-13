#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:42:55 2020

@author: peterwu
"""
import cv2
# import struct ## new
import pickle
from keras.models import load_model
import numpy as np
import tensorflow as tf
# import tornado
from tensorflow.compat.v1 import InteractiveSession

class fer_model():    
    def __init__(self):
        self.config = tf.ConfigProto()
        self.config.gpu_options.allow_growth = True
        self.sess = InteractiveSession(config=self.config)
        self.graph = tf.get_default_graph()
        # loading face detection model
        self.face_detection = cv2.CascadeClassifier('./model/haarcascade_frontalface_default.xml')
        # loading emo models
        self.emotion_classifier = load_model('./model/fer2013_mini_XCEPTION.102-0.66.hdf5', compile=False)
        self.emotion_offsets = (20, 40)
        # getting model output shape for inference
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]
        
    # @tornado.gen.coroutine
    def img_pre_processing(self, rev_message):
        frame = pickle.loads(rev_message, fix_imports=True, encoding="bytes")
        frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # @tornado.gen.coroutine
    def detect_faces(self, gray_image_array):
        return self.face_detection.detectMultiScale(gray_image_array, 1.3, 5)
    
    # @tornado.gen.coroutine
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
    
    # @tornado.gen.coroutine
    def emo_predict(self, gray_face):
        with self.graph.as_default():
            emo = self.emotion_classifier.predict(gray_face)
        return emo
    
    # @tornado.gen.coroutine
    def apply_offsets(self, face_coordinates, offsets):
        x, y, width, height = face_coordinates
        x_off, y_off = offsets
        return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)
    
    # @tornado.gen.coroutine
    def preprocess_input(self, x, v2=True):
        x = x.astype('float32')
        x = x / 255.0
        if v2:
            x = x - 0.5
            x = x * 2.0
        return x


