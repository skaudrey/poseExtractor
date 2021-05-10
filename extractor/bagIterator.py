#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : bagIterator.py
@ide    : PyCharm
@time   : 2021-05-03 16:08:44
@descrip: 
'''
import cv2
import pyrealsense2 as rs
from util.pathUtil import generate_imgName,extract_fname
import numpy as np
import os
from util.drawer import SkeletonDrawer

class BagIterator():
    '''
    Processing each bag file, including generate images and saving, extracting 2D pose and 3D pose.
    '''
    def __init__(self,extractor,aConfig):
        self._extractor = extractor
        self._kps_2d_dict = dict() # 2d pose dict, the key is image name and each value in shape (#subject,#data,#)
        self._kps_3d_dict = dict()
        self._intrinsic_dict = dict()
        self.aConfig = aConfig
        self._drawer = SkeletonDrawer()

    def extractPose(self,img,depth_map,depth_intrinsic):
        '''
        Extracting pose (2D and 3D) and return
        :param img: The image data, in cv2 format (BGR)
        :param depth_map: The depth_map from aligned depth frame
        :param depth_intrinsic: The depth intrinsic extracted from rosbag
        :return:kps_2d for 2D skeletons, kps_3d for 3D skeletons
        '''

        # extract 2D pose
        kps_2d = self._extractor.extract2DPose(img)
        # extract 3D pose
        if kps_2d is None:
            return None,None
        kps_3d = self._extractor.extract3DPose(kps_2d,depth_map,depth_intrinsic)
        return kps_2d,kps_3d


    def extraction(self):
        try:
            bag_ind = 0
            for filename in os.listdir(self.aConfig.BAG_PATH):
                # per bag, then per image, each bag has its intrinsic
                if filename.endswith('.bag'):
                    bag_fname = "%s/%s"%(self.aConfig.BAG_PATH,filename)
                    self._extract_from_bag(bag_fname)


                    bag_ind += 1
            print("Process bag files: %d"%bag_ind)
            return self._kps_2d_dict, self._kps_3d_dict,self._intrinsic_dict
        except RuntimeError:
            print("Unknown Error")
        finally:
            # release everything now that job finished
            cv2.destroyAllWindows()


    def _extract_from_bag(self,bag_fname):
        '''
        https://github.com/IntelRealSense/librealsense/issues/4934#issuecomment-537705225
        Extract images, depth map and intrinsic parameters from rosbag.
        Maintain the class attribute _kps_2d_dict,_kps_3d_dict, _intrinsic_dict,
        :param bag_fname: The name of bag file.
        :param img_path: The path to save extracted images.
        :param depth_path: The path to save extracted depth data.
        :return:
        '''

        config = rs.config()
        pipeline = rs.pipeline()

        # make it so the stream does not continue looping
        config.enable_stream(rs.stream.color)
        config.enable_stream(rs.stream.depth)
        rs.config.enable_device_from_file(config, bag_fname, repeat_playback=False)
        profile = pipeline.start(config)
        # this makes it so no frames are dropped while writing video
        playback = profile.get_device().as_playback()
        playback.set_real_time(False)

        colorizer = rs.colorizer()

        align_to = rs.stream.color
        align = rs.align(align_to)

        depth_sensor = profile.get_device().first_depth_sensor()
        # depth_scale = depth_sensor.get_depth_scale()

        # intrinsic = None

        i = 0
        try:
            while True:
                # when stream is finished, RuntimeError is raised, hence this
                # exception block to capture this
                try:
                    frames = pipeline.wait_for_frames()
                    # frames.keep()
                    # if you don't do keep, the frames can only be kept for 32 frames aka one cannot append
                    # aligned_depth_frame in memory, but with this, you may get OOM error.
                    if frames.size() < 2:
                        # Inputs are not ready yet
                        continue

                    # align the deph to color frame
                    aligned_frames = align.process(frames)
                    # aligned_frames.keep() # same reason as line 59 frames.keep()

                    # get aligned frames
                    aligned_depth_frame = aligned_frames.get_depth_frame()
                    color_frame = aligned_frames.get_color_frame()

                    # generate image name
                    color_fname = generate_imgName(extract_fname(bag_fname), i)
                    # depth_dict[color_fname] = aligned_depth_frame

                    # get depth intrinsic parameters
                    prof = aligned_depth_frame.get_profile().as_video_stream_profile()
                    intrinsic = prof.get_intrinsics()

                    # validate that both frames are valid
                    if not aligned_depth_frame or not color_frame:
                        continue

                    # generate color image
                    color_image_array = np.asanyarray(color_frame.get_data())  # seems the data got directly are BGR
                    # # convert color image to BGR for OpenCV
                    color_image = cv2.cvtColor(color_image_array, cv2.COLOR_RGB2BGR)
                    # r, g, b = cv2.split(color_image_array)
                    # color_image = cv2.merge((b, g, r))

                    # generate depth image
                    # depth_image = np.asanyarray(aligned_depth_frame.get_data())
                    # scaled_depth_image = depth_image * depth_scale
                    depth_colormap = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())

                    # extract pose and set up kps_dict
                    kps_2d, kps_3d = self.extractPose(color_image, aligned_depth_frame, intrinsic)
                    if kps_2d is None:  # if failed to detect keypoints, save the image to diff path
                        print("Cannot detect image -- %s" % (color_fname))
                        cv2.imwrite("%s/%s" % (self.aConfig.IMG_DIFF_SAVE_PATH, color_fname), color_image)
                    else:
                        self._kps_2d_dict[color_fname] = kps_2d
                        self._kps_3d_dict[color_fname] = kps_3d

                        # show image
                        if self.aConfig.SHOW_IMG_FLAG:
                            self.showImg(color_image, depth_colormap, kps_2d)

                        # save image
                        if self.aConfig.SAVE_IMAGE_FLAG:
                            cv2.imwrite("%s/%s" % (self.aConfig.IMG_SAVE_PATH, color_fname),
                                        color_image)

                    if cv2.waitKey(25) & 0xFF == ord('q'):
                        break

                    i += 1

                except (RuntimeError):
                    print('Processed frame count', i-1)
                    break
        except (RuntimeError):
            print("Error while processing one bag file")

        finally:
            pipeline.stop()

        # save depth maps
        bag_name = extract_fname(bag_fname)
        self._intrinsic_dict[bag_name] = \
            {"pp":[intrinsic.ppx,intrinsic.ppy],
             'focal': [intrinsic.fx, intrinsic.fy],
             "inv. Brown Conrady": intrinsic.coeffs}

        print(bag_name)

    def showImg(self,color_image, depth_colormap,skeletons_2d):
        # show image
        # img_show = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB) # the data form frame is BGR, to show it need to be RGB

        img_show = color_image # the data form frame is BGR, to show it need to be RGB
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
        skeleton_lines = self._drawer.drawSkeleton(self.aConfig.EXTRACTOR)
        for sub_ind in range(n_sub):
            skeleton = skeletons_2d[ind]
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

        cv2.namedWindow('Extract bag', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Extract bag', images)

