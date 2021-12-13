#!/usr/bin/env python
# pylint: disable=W0201
import sys
import argparse
import yaml
import numpy as np
import os
import torchlight
from torchlight import import_class

from torchlight import str2bool
from torchlight import DictAction
from util.drawer import SkeletonDrawer
import cv2
import json


class customIO():
    """
        IO Processor
    """

    def __init__(self, argv=None):
        self.arg = None
        self._extractor = None
        self._miss_skeleton_dict = {}  # store whether the video contain skeletons

        self.load_arg(argv)
        self.init_environment()
        self.init_extractor()


    def init_environment(self):
        self.io = torchlight.IO(
            self.arg.work_dir,
            save_log=self.arg.save_log,
            print_log=self.arg.print_log)
        self.io.save_arg(self.arg)

        self._drawer = SkeletonDrawer()

        self.parts = [ 'train','test']

        # build output path
        # skeletons
        for aPart in self.parts:
            apath = "%s/skeletons/%s" % (self.arg.output_path, aPart)
            if not os.path.exists(apath):
                os.makedirs(apath)

        # videos
        if self.arg.save_video:
            for aPart in self.parts:
                apath = "%s/video/%s" % (self.arg.output_path, aPart)
                if not os.path.exists(apath):
                    os.makedirs(apath)



    def load_arg(self, argv=None):
        parser = self.get_parser()

        # load arg form config file
        p = parser.parse_args(argv)
        if p.config is not None:
            # load config file
            with open(p.config, 'r') as f:
                default_arg = yaml.load(f, Loader=yaml.FullLoader)

            # update parser from config file
            key = vars(p).keys()
            for k in default_arg.keys():
                if k not in key:
                    print('Unknown Arguments: {}'.format(k))
                    assert k in key

            parser.set_defaults(**default_arg) # use loaded config.yml to set args in the parser
        self.arg = parser.parse_args(argv)

        self.arg.openpose_args['image_size'] = self.arg.image_size
        self.arg.cubemos_args['image_size'] = self.arg.image_size
        self.arg.posenet_args['image_size'] = self.arg.image_size
        self.arg.delay_cv = int(1000./(self.arg.fps*1.0))
        self.arg.submodel_name = self.arg.openpose_args['openpose_model'] if 'openpose_model' in self.arg.openpose_args.keys() else ""

    def init_extractor(self):
        if self.arg.model_name=="openpose":
            self._extractor = self.io.load_model(self.arg.extractor,
                                           **(self.arg.openpose_args))
        elif self.arg.model_name=='cubemos':
            self._extractor = self.io.load_model(self.arg.extractor,**(self.arg.cubemos_args))
        elif self.arg.model_name=='posenet':            self._extractor = self.io.load_model(self.arg.extractor, **(self.arg.posenet_args))

    def start(self):
        self.io.print_log('Parameters:\n{}\n'.format(str(vars(self.arg))))

    def selectTopKpose(self):
        '''
        use self.arg.max_subject_output
        :return:
        '''
        pass

    def showImg(self,color_image, depth_colormap,skeletons_2d):
        # show image
        img_show = color_image #
        n_sub,n_joint,dim = skeletons_2d.shape

        # show joints dots
        red = (0, 0, 255)
        green = (0,255,0)
        blue = (255,0,0)
        for ind in range(n_sub):
            skeleton = skeletons_2d[ind]
            for j_ind in range(n_joint):
                jx,jy = int(skeleton[j_ind][0]),int(skeleton[j_ind][1])
                if jx<=0 and jy<=0: # the undetected joint is denoted as 0,0 in openpose, and -1,-1 in cubemos
                    cv2.circle(img_show, center=(0,0), radius=4, color=red, thickness=-1)
                else:
                    cv2.circle(img_show,center = (jx,jy),radius = 4, color=green, thickness=-1 )

        # draw skeleton lines
        skeleton_lines = self._drawer.drawSkeleton(self.arg.model_name,self.arg.submodel_name)
        for sub_ind in range(n_sub):
            skeleton = skeletons_2d[sub_ind]
            #
            for i in range(len(skeleton_lines)): # each line
                aLine = skeleton_lines[i]

                for j in range(len(aLine)-1): # each subline
                    j1,j2 = aLine[j],aLine[j+1]

                    j1x,j1y = int(skeleton[j1][0]),int(skeleton[j1][1])
                    j2x, j2y = int(skeleton[j2][0]), int(skeleton[j2][1])

                    if((j1x<=0 and j1y<=0) or (j2x<=0 and j2y<=0)):
                        continue
                    else:
                        cv2.line(img_show, (j1x,j1y),(j2x,j2y), color=blue, thickness=2)

        images = img_show

        if depth_colormap is not None:
            images = np.hstack((img_show, depth_colormap))

        cv2.namedWindow('Extract video', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Extract video', images)

    def saveJson(self,part,video_id,data):
        apath = "%s/skeletons/%s" % (self.arg.output_path, part)
        if part=="":
            apath = "%s/skeletons" % (self.arg.output_path)

        # data = {k:v.tolist() for k,v in data.items()} # numpy array cannot be directly dumped, but list can be done
        with open("%s/%s.json" % (apath, video_id), 'w') as f:
            json.dump(data, f)

    @staticmethod
    def get_parser(add_help=False):

        #region arguments yapf: disable
        # parameter priority: command line > config > default
        parser = argparse.ArgumentParser( add_help=add_help, description='IO Processor')
        parser.add_argument("-c", "--config", type=str, default=os.getcwd() + "./config/bag_config.yml",
                            help="the path of config file")
        parser.add_argument("-w", "--work_dir", type=str, default=os.getcwd() + "./work_dir",
                            help="the path of work directory")
        # visulize and debug
        parser.add_argument('--print_log', type=str2bool, default=True, help='print logging or not')
        parser.add_argument('--save_log', type=str2bool, default=True, help='save logging or not')

        parser.add_argument("-i", "--input_path", type=str, default=os.getcwd() +"./vsi",
                            help="the path where .vsi file to be read")
        parser.add_argument("-o", "--output_path", type=str, default=os.getcwd() + '/output',
                            help="the path where the extracted pose will be saved")
        parser.add_argument("-e", "--extractor", type=str, default='openpose',
                            help="The extractor to be used for extraction. Candidates are [openposs, cubemos,posenet]")

        parser.add_argument("-mn", "--model_name", type=str, default='openpose',
                            help="the model name used for extraction")
        parser.add_argument( "--submodel_name", type=str, default='COCO',
                            help="the model name used for extraction")

        parser.add_argument('--openpose_args', action=DictAction, default=dict(),
                            help='arguments used for OPENPOSE. Candidates are [BODY_25, COCO, MPI]')
        parser.add_argument('--posenet_args', action=DictAction, default=dict(),
                            help="posenet model name for extraction, used for poseNetTooler. Candidates are [50,75,100,101]")
        parser.add_argument('--cubemos_args', action=DictAction, default=dict(),help="cubemos model arguments")
        parser.add_argument("-msi", "--max_subject", type=int, default=5,
                            help="The maximum subjects that are allowed to be detected ")
        parser.add_argument("-mso", "--max_subject_output", type=int, default=2,
                            help="The maximum subjects that are allowed to be outputed ")
        parser.add_argument("-sf", "--showFlag", type=bool, default=False,
                            help="Whether to show the video while extracting.")
        parser.add_argument("--save_video", type=bool, default=False,
                            help="Whether to save the video while interpreting rosbag")
        parser.add_argument('-size', "--image_size", type=list, default=[340, 256],
                            help="resize images into the given size")
        parser.add_argument('-f', "--fps", type=int, default=30,
                            help="change the fps of original video into the given size")
        parser.add_argument("-savef", "--saveImgFlag", type=bool, default=False,
                            help="Whether to save the extracted images of each video.")
        parser.add_argument('-d', "--delay_cv", type=int, default=-1,
                            help="the delay time while reading videos by cv2, to change the fps of original video")
        parser.add_argument('-mt', "--miss_thresh", type=int, default=50,
                            help="the minimum number of frames that have skeletons so to label video having skeletons")



        #endregion yapf: enable

        return parser
