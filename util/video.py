#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : video.py
@ide    : PyCharm
@time   : 2021-04-30 13:06:11
@descrip: Process video: like trim, counting, clipping, changing to imgs or combining image as videos
'''
import cv2
import os
import numpy as np

def video2Img(video_path, save_path,time_interval=1):
    '''
    Change video into images.
    :param video_path: Path of video
    :param save_path: path to save extracted images
    :param time_interval: take frames per time_interval.
    :return:
    '''
    vc = cv2.VideoCapture(video_path)  # read video
    ind = 1
    tmp = video_path.split("/")[-1]
    video_name = tmp.split(".")[0]

    if vc.isOpened():  # check whether the video is loaded
        rval, frame = vc.read()
    else:
        rval = False

    while rval:  # read frames
        rval, frame = vc.read()
        if (ind % time_interval == 0):  # save images per time_interval
            cv2.imwrite('%s/%s_%d.jpg'%(save_path,video_name,ind), frame)
        ind = ind + 1
        cv2.waitKey(1)
    vc.release()

def img2Video(img_path,save_path,fps=24,img_size=(640,800)):
    '''
    Transform images to videos and save it
    :param img_path: the path of video's images.
    :param save_path: The path to save the combined video, including the video name
    :param fps: The fps of new video.
    :param img_size: The size (height, width) of generated video
    :return:
    '''
    filelist = os.listdir(img_path)

    # fps = 24  # the video will be 24 fps
    # size = (640, 480)  # the image size of video that's gonna be generated
    # cv2.resize() can help resize

    video = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc('I', '4', '2', '0'), fps, img_size)

    for item in filelist:
        if item.endswith('.png') or item.endswith('jpg'): # find all images in the provided directory
            item = img_path + item
            img = cv2.imread(item)
            video.write(img)

    video.release()
    cv2.destroyAllWindows()

def resize(targetSize):
    pass

