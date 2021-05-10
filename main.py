#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : main.py
@ide    : PyCharm
@time   : 2021-05-02 12:33:18
@descrip: The main script of extracting 3d pose
'''
from config import Config
import os
import argparse
from extractor import OpenPoseExtractor, CubeMos,BagIterator
from util.pathUtil import saveDataAsPkl

def validate(args):
    if not os.path.exists(args.input_bagpath):
        print("Please make sure the bag file path exists.")
        exit(-1)
    try:
        if not os.path.exists(args.output_path):
            os.makedirs(args.output_path)
    except:
        print("Bad things happen while creating output path")
        exit(-1)

def set_config(args,aConfig):
    aConfig.BAG_PATH = args.input_bagpath
    aConfig.OUTPUT_PATH = args.output_path
    aConfig.EXTRACTOR = args.extractor
    aConfig.OPENPOSE_MODEL = args.model

    aConfig.NUITRACK_KEY = args.nuitrack_key

    aConfig.NET_RESOLUTION = args.net_resolution
    aConfig.FACE_RESOLUTION = args.face_net_resolution
    aConfig.HAND_RESOLUTION = args.hand_net_resolution


def initializeTmpPath(bag_path,aConfig):
    '''
    Check the path for saving images, if not exits, make it.
    :param bag_path: The path of bag file, image folder path is searched based on it.
    :return:
    '''
    img_path = "%s/../input/img"%bag_path
    img_diff_path = "%s/../input/img_diff"%bag_path

    if not os.path.exists(img_path):
        os.makedirs(img_path)
    if not os.path.exists(img_diff_path):
        os.makedirs(img_diff_path)
    img_diff_path = "%s/%s" % (img_diff_path,aConfig.EXTRACTOR.lower())
    if not os.path.exists(img_diff_path):
        os.makedirs(img_diff_path)

    aConfig.IMG_SAVE_PATH = img_path
    aConfig.IMG_DIFF_SAVE_PATH = img_diff_path

def initialize_extractor(aConfig):
    '''
    Initialize the extractor tool according to config.EXTRACTOR.
    :return: The instance of extractor.
    '''
    extractor = None
    if aConfig.EXTRACTOR == "OPENPOSE":
        extractor = OpenPoseExtractor(aConfig)
    elif aConfig.EXTRACTOR == "CUBEMOS":
        extractor = CubeMos(aConfig)
    elif aConfig.EXTRACTOR == "NUITRACK":
        pass

    return extractor

def main(args):

    # Check whether the input path and output path exist.
    validate(args)

    # set up config and save it as yaml file
    aConfig = Config()
    set_config(args,aConfig)
    # generate the image file folder (if not exists)
    initializeTmpPath(aConfig.BAG_PATH,aConfig)
    aConfig.writeConfig()

    # Get the instance of extractor.
    extractor = initialize_extractor(aConfig)

    # Get the instance of bag iterator.
    bagIter = BagIterator(extractor,aConfig)

    #Extract skeletons and intrinsic.
    kps_2d_dict, kps_3d_dict,intrinsic_dict = bagIter.extraction()

    # generate file name and save files.
    pose_3d_fname = '%s/kps-3d-%s.pkl' % ( aConfig.OUTPUT_PATH, aConfig.EXTRACTOR.lower() )
    pose_2d_fname = '%s/kps-2d-%s.pkl' % ( aConfig.OUTPUT_PATH, aConfig.EXTRACTOR.lower() )
    intrinsic_fname = '%s/intrinsic.pkl' % aConfig.OUTPUT_PATH
    saveDataAsPkl(kps_2d_dict,pose_2d_fname)
    saveDataAsPkl(kps_3d_dict,pose_3d_fname)
    saveDataAsPkl(intrinsic_dict,intrinsic_fname)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_bagpath", type=str, default=os.getcwd()+'/bag', help="the path where .bag file to be read")
    parser.add_argument("-o", "--output_path", type=str, default=os.getcwd()+'/output', help="the path where the extracted pose will be saved")
    parser.add_argument("-e", "--extractor", type=str, default='CUBEMOS', help="The extractor to be used for extraction. Candidates are [OPENPOSE, CUBEMOS]")
    parser.add_argument("-mp", "--model", type=str, default='BODY_25',help="model name for extraction, used for OPENPOSE. Candidates are [BODY_25, COCO_18, MPI]")
    parser.add_argument("-opdir", "--openpose_dir", type=str, default='D:/work/openpose/build',
                        help="The directory of openpose build folder.")
    parser.add_argument("-res", "--net_resolution", type=str, default='-1x256',
                        help="The resolution while detecting with openpose.")
    parser.add_argument("-face_res", "--face_net_resolution", type=str, default='256x256',
                        help="The face resolution while detecting with openpose.")
    parser.add_argument("-hand_res", "--hand_net_resolution", type=str, default='256x256',
                        help="The hand resolution while detecting with openpose.")
    parser.add_argument("-ckey","--cubemos_key",type=str, default="",help="the activation key of cubemos")
    parser.add_argument("-nkey","--nuitrack_key",type=str, default="license:25718:VW4FdmeyQ74fM7PH",help="the activation key of nuitrack")

    args = parser.parse_args()

    main(args)









