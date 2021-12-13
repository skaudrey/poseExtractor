#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : poseNetTooler.py
@ide    : PyCharm
@time   : 2021-06-11 11:28:15
@descrip: 
'''

from .baseExtractor import BaseExtractor
import numpy as np
from extractor import poseNetTooler
import torch
from util.video import process_input

class PoseNet(BaseExtractor):
    '''
    Use Posenet Model and return 18 joints.
    https://github.com/rwightman/posenet-pytorch
    '''
    def __init__(self,scale_factor, posenet_model,joint_confidence=0.3,image_size = (340,256,3)):
        print("Initialize posenet extractor")
        # Initialize the openpose model
        # self._aConfig = aConfig
        self.joint_confidence = joint_confidence
        self.max_subject = 5
        self.image_size = image_size
        self.scale_factor = scale_factor
        self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        self.extractor = poseNetTooler.load_model(posenet_model)
        self.extractor = self.extractor.to(self.device)

        self.input_image = None

        self.output_stride = self.extractor.output_stride

    def read_imgfile(self,img):
        '''
        Convert the original image data: resize and rescale.
        :param img:
        :return: the processed input image for posenet (resize and normalization)
        '''
        return process_input(img, self.scale_factor, self.output_stride)

    def extract2DPose(self,img_data):
        '''
        :param img_data: should be numpy ndarray
        :return:
        '''
        # self.extractor =
        # preprocess read image: resize and normalization
        i_image, output_scale = self.read_imgfile(img_data)

        with torch.no_grad():
            self.input_image = torch.Tensor(i_image).to(self.device)
            heatmaps_result, offsets_result, displacement_fwd_result, displacement_bwd_result = \
                self.extractor(self.input_image)

            pose_scores, keypoint_scores, keypoint_coords = poseNetTooler.decode_multiple_poses(
                heatmaps_result.squeeze(0),
                offsets_result.squeeze(0),
                displacement_fwd_result.squeeze(0),
                displacement_bwd_result.squeeze(0),
                output_stride=self.output_stride,
                max_pose_detections=self.max_subject,
                min_pose_score=self.joint_confidence)

        keypoint_coords *= output_scale # in shape (1,18,2)
        keypoint_coords = keypoint_coords[:,:,[1,0]]

        keypoint_scores = np.expand_dims(keypoint_scores,axis=2) # expand to (1,18,1)

        kps_coords_scores = np.concatenate((keypoint_coords,keypoint_scores),axis=2) # concatenate to (1,18,3)

        if np.all(kps_coords_scores.astype(np.int) == 0): # when the frame is empty, return None
            kps_coords_scores = None

        return kps_coords_scores

    def clean(self):
        try:
            del self.input_image
            del self.extractor

            self.extractor = poseNetTooler.load_model(self._aConfig.POSENET_MODEL)
            self.extractor = self.extractor.to(self.device)

            self.input_image = None
        except ImportError:
            print("Import error")


if __name__ == "__main__":
    pass


