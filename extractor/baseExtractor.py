#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : baseExtractor.py
@ide    : PyCharm
@time   : 2021-05-03 16:49:29
@descrip: 
'''
import numpy as np
import pyrealsense2 as rs
import math

class BaseExtractor(object):
    def __init__(self):
        pass

    def extract2DPose(self,img_data):
        pass

    def extract3DPose(self,skeletons_2d, depth_map, depth_intrinsic):
        '''
        Use the extracted 2d pose from RGB images and depth map, detect 3D pose.
        NOTE: the keypoints struct are different from different extractor.
        :param skeletons_2d: The extracted 2d pose in shape (#subject,
        #keypoints, 3), where 3 means x,y dimension and confidence score.
        :param depth_map: The depth map from RGBD camera (extracted from saved vsi file)
        :param depth_intrinsic: The intrinsic parameters of camera.
        :param joint_confidence: The threshold of keypoint confidence score.
        :return: The extracted 3D pose and confidence score
        '''
        # thickness = 1
        # text_color = (255, 255, 255)
        rows, cols, channel = self.image_size
        distance_kernel_size = 5
        # calculate 3D keypoints and display them
        subject_n, joint_n, dim = skeletons_2d.shape
        pts_3d = np.ndarray((subject_n, joint_n, 4)) # shape 4 is x,y,z and score
        for skeleton_index in range(subject_n):
            skeleton_2D = skeletons_2d[skeleton_index]
            joints_2D = skeleton_2D

            for joint_index in range(joint_n):

                # check if the joint was detected and has valid coordinate
                joint_x, joint_y, j_confidence = joints_2D[joint_index, ]

                if j_confidence > self.joint_confidence:
                    distance_in_kernel = []  # the next get torso box?
                    low_bound_x = max(
                        0,
                        int(joint_x - math.floor(distance_kernel_size / 2)),
                    )
                    upper_bound_x = min(
                        cols - 1,
                        int(joint_x + math.ceil(distance_kernel_size / 2)),
                    )
                    low_bound_y = max(
                        0,
                        int(joint_y - math.floor(distance_kernel_size / 2)),
                    )
                    upper_bound_y = min(
                        rows - 1,
                        int(joint_y + math.ceil(distance_kernel_size / 2)),
                    )

                    for x in range(low_bound_x, upper_bound_x):
                        for y in range(low_bound_y, upper_bound_y):
                            distance_in_kernel.append(depth_map.get_distance(x, y))
                    median_distance = np.percentile(np.array(distance_in_kernel), 50)
                    depth_pixel = [int(joint_x), int(joint_y)]

                    if median_distance >= 0.3:
                        point_3d = rs.rs2_deproject_pixel_to_point(
                            depth_intrinsic, depth_pixel, median_distance
                        )
                        # Deprojection takes a 2D pixel location on a stream's images, as well as a depth,
                        # specified in meters, and maps it to a 3D point location within the stream's associated
                        # 3D coordinate space.
                        point_3d = np.round([float(i) for i in point_3d], 3)
                        pts_3d[skeleton_index, joint_index, [0, 1, 2]] = point_3d
                        pts_3d[skeleton_index, joint_index, -1] = j_confidence
                else:
                    # set the default value when the joint is not reliable
                    point_3d = np.array([1e-5]*3)
                    pts_3d[skeleton_index, joint_index, [0, 1, 2]] = point_3d
                    pts_3d[skeleton_index, joint_index, -1] = -1.

        return pts_3d



    def validatePoses(self,multi_pose):
        # normalization
        # multi_pose[:, :, 0] = multi_pose[:, :, 0] / W
        # multi_pose[:, :, 1] = multi_pose[:, :, 1] / H
        # multi_pose[:, :, 0:2] = multi_pose[:, :, 0:2] - 0.5
        multi_pose[:, :, 0][multi_pose[:, :, 2] == 0] = 0
        multi_pose[:, :, 1][multi_pose[:, :, 2] == 0] = 0  # if score==0, set joint from zero point
        return multi_pose


    def clean(self):
        pass