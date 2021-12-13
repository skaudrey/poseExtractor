#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : main_old.py
@ide    : PyCharm
@time   : 2021-05-02 12:33:18
@descrip: The main script of extracting 3d pose
'''
from config import Config
import os
import argparse
from extractor import OpenPoseExtractor, CubeMos,PoseNet
from process import BagIterator,VideoIterator
from util.pathUtil import saveData

def validate(args):
    if not (os.path.exists(args.input_bagpath) or os.path.exists(args.input_vpath)):
        print("Please make sure the input file path exists.")
        exit(-1)
    try:
        if not os.path.exists(args.output_path):
            os.makedirs(args.output_path)
    except:
        print("Bad things happen while creating output path")
        exit(-1)

def set_config(args,aConfig):
    aConfig.BAG_PATH = args.input_bagpath
    aConfig.VIDEO_PATH = args.input_vpath
    aConfig.OUTPUT_PATH = args.output_path
    aConfig.EXTRACTOR = args.extractor
    aConfig.OPENPOSE_MODEL = args.op_model
    aConfig.POSENET_MODEL = args.pn_model

    aConfig.NET_RESOLUTION = args.net_resolution
    aConfig.FACE_RESOLUTION = args.face_net_resolution
    aConfig.HAND_RESOLUTION = args.hand_net_resolution

    aConfig.MAX_POSE = args.max_subject
    # aConfig.MAX_POSE_OUT = args.max_subject_output
    # aConfig.SCALE_FACTOR = args.scale
    aConfig.FPS = args.fps
    aConfig.IMAGE_SIZE = args.image_size
    aConfig.DELAY_CV = int(1000./(aConfig.FPS*1.0))

    # flag
    aConfig.SHOW_IMG_FLAG = args.showFlag
    aConfig.SAVE_IMAGE_FLAG = args.saveImgFlag

    # joint confidence score
    aConfig.JOINT_CONFIDENCE = args.joint_confidence


def initializeTmpPath(bag_path,aConfig):
    '''
    Check the path for saving images, if not exits, make it.
    :param bag_path: The path of vsi file, image folder path is searched based on it.
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
    elif aConfig.EXTRACTOR == "POSENET":
        extractor = PoseNet(aConfig)

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

    # Get the instance of vsi iterator.
    dataIter = BagIterator(extractor,aConfig)
    if aConfig.BAG_PATH == ".":
        dataIter = VideoIterator(extractor,aConfig)

    #Extract skeletons and intrinsic.
    kps_2d_dict, kps_3d_dict,bags_info_dict,fail_imgs,miss_skeleton_videos = dataIter.extraction()

    # generate file name and save files.
    pose_3d_fname = '%s/kps-3d-%s.pkl' % ( aConfig.OUTPUT_PATH, aConfig.EXTRACTOR.lower() )
    pose_2d_fname = '%s/kps-2d-%s.pkl' % ( aConfig.OUTPUT_PATH, aConfig.EXTRACTOR.lower() )
    bags_info_fname = '%s/bags_info.pkl' % aConfig.OUTPUT_PATH
    # fail_imgs_fname = '%s/missing_skeletons_images.txt' % aConfig.OUTPUT_PATH
    miss_skeleton_fname = '%s/missing_skeletons_videos.txt' % aConfig.OUTPUT_PATH
    saveData(kps_2d_dict,pose_2d_fname)
    saveData(kps_3d_dict,pose_3d_fname)
    if bags_info_dict is not None:
        saveData(bags_info_dict,bags_info_fname)
    # saveData(fail_imgs,fail_imgs_fname)
    saveData(miss_skeleton_fname, miss_skeleton_videos) # save the id of videos that missing skeletons


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_bagpath", type=str, default=os.getcwd()+'/vsi', help="the path where .vsi file to be read")
    parser.add_argument("-iv", "--input_vpath", type=str, default=os.getcwd() + '/video',
                        help="the path where video files to be read")
    parser.add_argument("-o", "--output_path", type=str, default=os.getcwd()+'/output', help="the path where the extracted pose will be saved")
    parser.add_argument("-e", "--extractor", type=str, default='OPENPOSE', help="The extractor to be used for extraction. Candidates are [OPENPOSE, CUBEMOS,POSENET]")
    parser.add_argument("-mp", "--op_model", type=str, default='COCO',help="openpose model name for extraction, used for OPENPOSE. Candidates are [BODY_25, COCO_18, MPI]")
    parser.add_argument("-opdir", "--openpose_dir", type=str, default='D:/work/openpose/build',
                        help="The directory of openpose build folder.")
    parser.add_argument("-mpn", "--pn_model", type=int, default=101,help="poseNetTooler model name for extraction, used for poseNetTooler. Candidates are [50,75,100,101]")
    parser.add_argument("-res", "--net_resolution", type=str, default='-1x256',
                        help="The resolution while detecting with openpose.")
    parser.add_argument("-face_res", "--face_net_resolution", type=str, default='256x256',
                        help="The face resolution while detecting with openpose.")
    parser.add_argument("-hand_res", "--hand_net_resolution", type=str, default='256x256',
                        help="The hand resolution while detecting with openpose.")
    parser.add_argument("-msi","--max_subject",type=int,default=5,help="The maximum subjects that are allowed to be detected ")
    # parser.add_argument("-mso", "--max_subject_output", type=int, default=2,
    #                     help="The maximum subjects that are allowed to be outputed ")
    # parser.add_argument("-s","--scale",type=float,default=1.0,help="The scale factor of input images for posenet")
    parser.add_argument("-sf","--showFlag",type=bool,default=False,help="Whether to show the video while extracting.")
    parser.add_argument('-jf',"--joint_confidence",type=float,default=0.3,help="The threshold of joint confidence score.")
    parser.add_argument('-size',"--image_size",type=list,default=[340,256],help="resize images into the given size")
    parser.add_argument('-f', "--fps", type=int, default=30, help="change the fps of original video into the given size")
    parser.add_argument("-savef","--saveImgFlag",type=bool,default=False,help="Whether to save the extracted images of each video.")

    args = parser.parse_args()

    main(args)









