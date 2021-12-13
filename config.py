#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : config.py
@ide    : PyCharm
@time   : 2021-05-02 12:52:02
@descrip: 
'''
import os
import yaml

class Config():
    def __init__(self):
        self.BAG_PATH = "%s/vsi" % (os.getcwd())
        self.VIDEO_PATH = "%s/video" % (os.getcwd())
        self.OUTPUT_PATH = "%s/../output" % self.BAG_PATH
        self.IMG_SAVE_PATH = "%s/../input/img" % self.BAG_PATH  # The default save path
        self.IMG_DIFF_SAVE_PATH = "%s/../input/img_diff" % self.BAG_PATH  # The default save path for failed image

        # openpose
        self.EXTRACTOR = "OPENPOSE"  # or extractor = "CUBEMOS"

        self.OPENPOSE_ROOT_DIR = "D:/work/openpose/build"

        self.OPENPOSE_MODEL = "BODY_25"
        self.POSENET_MODEL = 101
        self.NET_RESOLUTION = '-1x128'
        self.FACE_RESOLUTION = '128x128'
        self.HAND_RESOLUTION = '128x128'

        # image and joint threshold
        self.IMAGE_SIZE = (720, 1280)

        self.JOINT_CONFIDENCE = 0.3  # The threshold of joint confidence, joint with confidence > JOINT_CONFIDENCE are accepted.

        self.SAVE_IMAGE_FLAG = False  # Whether to save images to <IMG_SAVE_PATH> while extracting them from rosbag.
        self.SHOW_IMG_FLAG = True  # Whether show the images while extracting them from rosbag.

        self.MAX_POSE = 5 # The maximum subjects allowed to be detected.
        # self.MAX_POSE_OUT = 2 # The maximum subjects allowed to be outputed.

        # self.SCALE_FACTOR = 1.0 # the scale factor

        # fps
        self.FPS = 30
        self.DELAY_CV = int(1000./self.FPS*1.0) # delay

    def writeConfig(self):
        filepath = '%s/config.yml'%self.OUTPUT_PATH

        outDict = dict()

        op_keys = ['BAG_PATH','OUTPUT_PATH','IMG_SAVE_PATH','IMG_DIFF_SAVE_PATH','EXTRACTOR',
                   'OPENPOSE_ROOT_DIR','OPENPOSE_MODEL','NET_RESOLUTION','FACE_RESOLUTION',
                   'HAND_RESOLUTION','IMAGE_SIZE','JOINT_CONFIDENCE','VIDEO_PATH',
                   'MAX_POSE',]
        posenet_keys = ['BAG_PATH','OUTPUT_PATH','IMG_SAVE_PATH','IMG_DIFF_SAVE_PATH','EXTRACTOR',
                        'POSENET_MODEL','IMAGE_SIZE','JOINT_CONFIDENCE','MAX_POSE','SCALE_FACTOR']
        cb_keys = ['BAG_PATH','OUTPUT_PATH','IMG_SAVE_PATH','IMG_DIFF_SAVE_PATH','EXTRACTOR',
                   'IMAGE_SIZE','JOINT_CONFIDENCE','VIDEO_PATH']


        outDict['BAG_PATH'] = self.BAG_PATH
        outDict['VIDEO_PATH'] = self.VIDEO_PATH
        outDict['OUTPUT_PATH'] = self.OUTPUT_PATH
        outDict['IMG_SAVE_PATH'] = self.IMG_SAVE_PATH
        outDict['IMG_DIFF_SAVE_PATH'] = self.IMG_DIFF_SAVE_PATH
        outDict['EXTRACTOR'] = self.EXTRACTOR
        outDict['OPENPOSE_ROOT_DIR'] = self.OPENPOSE_ROOT_DIR
        outDict['OPENPOSE_MODEL'] = self.OPENPOSE_MODEL
        outDict['NET_RESOLUTION'] = self.NET_RESOLUTION
        outDict['FACE_RESOLUTION'] = self.FACE_RESOLUTION
        outDict['HAND_RESOLUTION'] = self.HAND_RESOLUTION
        outDict['IMAGE_SIZE'] = self.IMAGE_SIZE
        outDict['JOINT_CONFIDENCE'] = self.JOINT_CONFIDENCE
        outDict['POSENET_MODEL'] = self.POSENET_MODEL
        # outDict['SCALE_FACTOR'] = self.SCALE_FACTOR
        outDict['MAX_POSE'] = self.MAX_POSE
        # outDict['MAX_POSE_OUT'] = self.MAX_POSE_OUT
        outDict['FPS'] = self.FPS
        outDict['DELAY_CV'] = self.DELAY_CV


        from operator import itemgetter
        with open(filepath, 'w') as f:
            if self.EXTRACTOR == "OPENPOSE":
                tmp_dict = {key: value for key, value in outDict.items() if key in op_keys}
                yaml.dump(tmp_dict, f)
            elif self.EXTRACTOR == "CUBEMOS":
                tmp_dict = {key: value for key, value in outDict.items() if key in cb_keys}
                yaml.dump(tmp_dict, f)
            elif self.EXTRACTOR == "POSENET":
                tmp_dict = {key: value for key, value in outDict.items() if key in posenet_keys}
                yaml.dump(tmp_dict, f)
















