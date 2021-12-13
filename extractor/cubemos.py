#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : cubemos.py
@ide    : PyCharm
@time   : 2021-04-29 23:41:25
@descrip:

Before using cubemos, set environment variables

'''

from .skeletontracker import skeletontracker
from .baseExtractor import BaseExtractor
import numpy as np

class CubeMos(BaseExtractor):
    '''
    Use Cubemos Model and return 18 joints.
    https://cubemos.stoplight.io/
    '''
    def __init__(self,joint_confidence=0.3,image_size = (340,256,3)):
        print("Initialize cubemos extractor")
        # Initialize the cubemos api with a valid license key in default_license_dir()
        self.joint_confidence = joint_confidence
        self.image_size = image_size
        self.extractor = skeletontracker(cloud_tracking_api_key="")


    def extract2DPose(self,img_data):
        '''
        :param img_data: should be numpy ndarray
        :return:
        '''

        skeletons = self.extractor.track_skeletons(img_data)  # so only color images are used?

        return self.cubeSkeleton2Array(skeletons)

    def cubeSkeleton2Array(self,skeletons_2d):
        '''
        Change the generated cubemos 2d skeletons to
        :param skeletons_2d: the cubemos skeletons, the struct description file is
        [here](https://cubemos.stoplight.io/docs/skeleton-estimation/reference/Skeleton-Estimation.v1.yaml/paths/~1estimate/post)
        The 2D skeletons are manages as shape (#subject,#joints, 3)
        Orderly, the joints are
        [   nose, neck,
            right_shoulder, right_elbow, right_wrist,
            left_shoulder, left_elbow, left_wrist,
            right_hip, right_knee, right_ankle,
            left_hip, left_knee, left_ankle,
            right_eye, left_eye,
            right_ear, left_ear
        ]
        :return:
        '''
        if len(skeletons_2d)==0:
            return None
        subject_n, joints_n = len(skeletons_2d), len(skeletons_2d[0].joints)
        kps_array = np.ndarray((subject_n,joints_n,3)) # 3 means x,y and confidence
        for skeleton_index in range(subject_n): # loop on each detected subject
            skeleton_2D = skeletons_2d[skeleton_index]
            joints_2D = skeleton_2D.joints
            for joint_index in range(joints_n):
                # extract joint coordinates and confidence score.
                joint_x, joint_y = joints_2D[joint_index].x, joints_2D[joint_index].y
                j_confidence = skeleton_2D.confidences[joint_index]

                # set the kps_array
                kps_array[skeleton_index, joint_index, 0] = joint_x
                kps_array[skeleton_index, joint_index, 1] = joint_y
                kps_array[skeleton_index, joint_index, -1] = j_confidence
        return kps_array


