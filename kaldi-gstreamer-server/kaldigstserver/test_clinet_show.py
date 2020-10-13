#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 19:14:14 2020

@author: peterwu
"""

import cv2
box = []
cap = cv2.VideoCapture('/home/peterwu/d_disk/FER_for_borris/video_/Test.mp4')
while(cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # print(frame)
    if frame is None:
        break
    frame = cv2.resize(frame,(600,480))
    box.append(frame)
    # print(frame.shape)
    # cap.set(3, 640)
    # cap.set(4, 480)
    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2BRG)

    # Display the resulting frame
    # cv2.imshow('frame',frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break
#%%
for i, fr in enumerate(box):
    if i % 2 == 0:
        print(i)
        cv2.imshow('frame',fr)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
