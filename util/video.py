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
import win32api, win32con
import math

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

def getScreenResolution():

    res_x = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)  # screen resolution in x axis

    res_y = win32api.GetSystemMetrics(win32con.SM_CYSCREEN) # screen resolution in y axis

    return [res_x,res_y]

def resize(img,targetSize,joints_list):
    raw_size = img.shape[:2]

    scale_x = raw_size[0]/targetSize[0]
    scale_y = raw_size[1]/targetSize[1]

    resized_joints = []
    i = 0

    for idx,joint in enumerate(joints_list):
        r_x, r_y = math.ceil(joint[0]*scale_x),math.ceil(joint[1]*scale_y)
        resized_joints[idx] = np.array([r_x,r_y])

    img_resize = cv2.resize(img, targetSize)

    return img_resize,resized_joints


def valid_resolution(width, height, output_stride=16):
    '''
    Check whether the required resolution is satisfied.
    '''
    # Why +1?
    # target_width = (int(width) // output_stride) * output_stride + 1
    # target_height = (int(height) // output_stride) * output_stride + 1

    target_width = (int(width) // output_stride) * output_stride
    target_height = (int(height) // output_stride) * output_stride

    return target_width, target_height

def process_input(source_img, scale_factor=1.0, output_stride=16):
    '''
    The source image is read by cv2.
    '''
    target_width, target_height = valid_resolution(
        source_img.shape[1] * scale_factor, source_img.shape[0] * scale_factor, output_stride=output_stride)
    scale = np.array([source_img.shape[0] / target_height, source_img.shape[1] / target_width])

    input_img = cv2.resize(source_img, (target_width, target_height), interpolation=cv2.INTER_LINEAR)
    input_img = cv2.cvtColor(input_img, cv2.COLOR_BGR2RGB).astype(np.float32)
    input_img = input_img * (2.0 / 255.0) - 1.0
    input_img = input_img.transpose((2, 0, 1)).reshape( 1, 3, target_height, target_width)
    return input_img, scale