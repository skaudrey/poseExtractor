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
        self.BAG_PATH = "%s/bag" % (os.getcwd())
        self.OUTPUT_PATH = "%s/../output" % self.BAG_PATH
        self.IMG_SAVE_PATH = "%s/../input/img" % self.BAG_PATH  # The default save path
        self.IMG_DIFF_SAVE_PATH = "%s/../input/img_diff" % self.BAG_PATH  # The default save path for failed image

        # openpose
        self.EXTRACTOR = "OPENPOSE"  # or extractor = "CUBEMOS"

        self.OPENPOSE_ROOT_DIR = "D:/work/openpose/build"

        self.OPENPOSE_MODEL = "BODY_25"
        self.NET_RESOLUTION = '-1x128'
        self.FACE_RESOLUTION = '128x128'
        self.HAND_RESOLUTION = '128x128'

        # activation key of charged pose extractor
        # self.CUBEMOS_KEY = ""
        self.NUITRACK_KEY = ""

        # image and joint threshold
        self.IMAGE_SIZE = [720, 1280, 3]

        self.JOINT_CONFIDENCE = 0.3  # The threshold of joint confidence, joint with confidence > JOINT_CONFIDENCE are accepted.

        self.SAVE_IMAGE_FLAG = True  # Whether to save images to <IMG_SAVE_PATH> while extracting them from rosbag.
        self.SHOW_IMG_FLAG = True  # Whether show the images while extracting them from rosbag.

    def writeConfig(self):
        filepath = '%s/config.yml'%self.OUTPUT_PATH

        outDict = dict()

        outDict['BAG_PATH'] = self.BAG_PATH
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

        with open(filepath, 'w') as f:
            yaml.dump(outDict, f)















