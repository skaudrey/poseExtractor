#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : read_kps.py
@ide    : PyCharm
@time   : 2021-04-29 14:47:01
@descrip: OpenPose extractor
'''
# From Python
# It requires OpenCV installed for Python
import sys
import os
from sys import platform
from .baseExtractor import BaseExtractor

class OpenPoseExtractor(BaseExtractor):
    '''
    Each time
    '''
    def __init__(self,aConfig):
        '''
        Initialize the openpose Extractor.
        :param openpose_rootdir: Where the built openpose exits
        :param model_pose: the pose model. Openpose supports [BODY_25, COCO, MPI], but BODY_25 with highest performance.
        '''
        print("Initialize openpose extractor")
        self._aConfig = aConfig
        self._dir_path = aConfig.OPENPOSE_ROOT_DIR
        self._model_pose = aConfig.OPENPOSE_MODEL

        # import openpose and then set the parameters
        try:
            # Windows Import
            if platform == "win32":
                # Change these variables to point to the correct folder (Release/x64 etc.)
                print(self._dir_path + '/python/openpose/Release')
                sys.path.append(self._dir_path + '/python/openpose/Release')
                os.environ['PATH'] = os.environ['PATH'] + ';' + self._dir_path + '/x64/Release;' + self._dir_path + '/bin;'
                import pyopenpose as op
            else:
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append('../work/openpose-master/python')
                # If you run `make install` (default path is `/usr/local/python` for Ubuntu),
                # you can also access the OpenPose/python module from there. This will install OpenPose and the
                # python library at your desired installation path. Ensure that this is in your python path in order
                # to use it.
                # sys.path.append('/usr/local/python')
                from openpose import pyopenpose as op
                from op import Vecotr
        except ImportError as e:
            print(
                'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e

        # set other parameters
        params = dict()
        params["model_folder"] = self._dir_path + "/../models"
        # print(self._dir_path + "/../models")
        params['model_pose'] = self._model_pose

        params['net_resolution'] = aConfig.NET_RESOLUTION
        params['face_net_resolution'] = aConfig.FACE_RESOLUTION
        params['hand_net_resolution'] = aConfig.FACE_RESOLUTION
        self._params = params

        # Starting OpenPose and instancing the used functions and data structs from openpose
        # I am only doing this because the imported op cannot be recognized out of __init__ (where I import op)
        # therefore all used are initialized here. But there maybe better way to do this.
        self._opWrapper = op.WrapperPython()
        self._opWrapper.configure(self._params)
        self._opWrapper.start()
        self._datum = op.Datum()
        self._opFunction = lambda datum: op.VectorDatum([datum])

    def extract2DPose(self,img_data):
        '''
        Note the img_data is read by cv2 (default), aka the order of channel is BGR
        :param img_data:
        :return:
        '''
        self._datum.cvInputData = img_data
        # self._opWrapper.emplaceAndPop(self._opFunction(self._datum))
        self._opWrapper.emplaceAndPop(self._opFunction(self._datum))

        skeletons = self._datum.poseKeypoints
        return skeletons

    def postProcess_skeleton(self,skeleton_2d):
        '''
        May can delete the impossible subject
        :param skeleton_2d:
        :return:
        '''
        n_subject = skeleton_2d.shape[0]
        for ind in range(n_subject):
            joints_2d = skeleton_2d[ind,:,:]
            if joints_2d[:,2]>self._aConfig.JOINT_CONFIDENCE:
                continue
            else:
                pass

    def clean(self):
        try:
            import pyopenpose as op

            del self._opWrapper
            del self._datum

            self._opWrapper = op.WrapperPython()
            self._opWrapper.configure(self._params)
            self._opWrapper.start()
            self._datum = op.Datum()
            self._opFunction = lambda datum: op.VectorDatum([datum])
        except ImportError:
            print("Import error")




if __name__=="__main__":
    dir_base = os.getcwd()
    print(dir_base)
    extractor = OpenPoseExtractor(dir_base+"/../bag",dir_base+"/../output/")

