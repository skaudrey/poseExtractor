#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : bagProcessor.py
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
import time
from process.customIO import customIO
import skvideo.io
from feeder.kinetics_gendata import gendata

class BagIterator(customIO):
    '''
    Processing each vsi file, including generate images and saving, extracting 2D pose and 3D pose.
    '''
    def __init__(self,argv):
        self.load_arg(argv)
        self.init_environment()
        self.init_extractor()

        self.video_info = dict()

        self.C,self.T,self.V = 4,400,18

    def extractInfo(self, bagFName):
        '''
        The files have names similar to this: `20210327_115917_p2s11r1e2.vsi`, among which, `20210327` represents the
        acquisition date March 27, 2021, `115917` represents the time 11:59 and lasts for 17 seconds, `p2s11r1e2`
        represents phase 2 scenario 11 repetition 1 student 2.
        :param bagFName:
        :return:
        '''
        tmp = bagFName.split("_")

        bag_fid = tmp[0] +"_"+tmp[1]

        phase = int(tmp[2][tmp[2].find("p")+1:tmp[2].find("s")])

        scenario = int(tmp[2][ tmp[2].find("s")+1:tmp[2].find("r") ]) # action label

        repeat = int(tmp[2][ tmp[2].find("r")+1:tmp[2].find("e") ])

        subject = int(tmp[2][ tmp[2].find("e")+1:tmp[2].find(".")])

        return bag_fid, phase, scenario, subject

    def extractPose(self,img,depth_map,depth_intrinsic):
        '''
        Extracting pose (2D and 3D) and return
        :param img: The image data, in cv2 format (BGR)
        :param depth_map: The depth_map from aligned depth frame
        :param depth_intrinsic: The depth intrinsic extracted from rosbag
        :return:kps_2d for 2D skeletons, kps_3d for 3D skeletons
        '''

        # extract 2D pose
        try:
            kps_2d = self._extractor.extract2DPose(img)
            # extract 3D pose
            if kps_2d is None:
                return None,None
            kps_3d = self._extractor.extract3DPose(kps_2d,depth_map,depth_intrinsic)

            return kps_2d,kps_3d
        except RuntimeError:
            print("An error happen when extract 3d pose, extractPose function")

    def start(self):
        '''
        Iterate each vsi and do extraction by call self._extract_from_bag(*).
        :return: self._kps_2d_dict, self._kps_3d_dict,self._bags_info_dict
        '''
        # for aPart in self.parts:
        #     print(aPart)
        #     bag_ind = 0
        #     self._miss_skeleton_dict = {}
        #     apath = self.arg.input_path + "/" + aPart
        #     for filename in os.listdir(apath):
        #         # per vsi, then per image, each vsi has its intrinsic
        #         if filename.endswith('.bag'):
        #             # print("Process vsi file: %d" % bag_ind)
        #             bag_fid, phase, scenario, subject = self.extractInfo(filename)
        #
        #             bag_fname = "%s/%s" % (apath, filename)
        #             miss_flag,poses_frames,video = self._extract_from_bag(bag_fname)
        #             print("End process vsi file: %d" % bag_ind)
        #
        #             # get data and save to json
        #             self.video_info['data'] = poses_frames
        #             self.video_info['label_index'] = scenario
        #             self.video_info['label_anomaly'] = phase
        #             self.saveJson(aPart, bag_fid, self.video_info)
        #
        #             if self.arg.save_video:
        #                 skvideo.io.vwrite("%s/video/%s/%s.mp4" % (self.arg.output_path, aPart, bag_fid),
        #                                   video,
        #                                   outputdict={"-pix_fmt": "yuv420p"})
        #
        #             self._miss_skeleton_dict[bag_fid] = {
        #                 'label_index': scenario,
        #                 'label_anomaly': phase,
        #                 'has_skeleton': miss_flag}
        #
        #             bag_ind += 1
        #         else:
        #             continue
        #     self.saveJson("", "%s_label"%aPart, self._miss_skeleton_dict)
        self.postProcess()


    def postProcess(self):
        output_path = "%s/skeletons/data"%self.arg.output_path
        print("T: %d"%self.T)
        for p in self.parts:
            data_path = '{}/skeletons/{}'.format(self.arg.output_path, p)
            label_path = '{}/skeletons/{}_label.json'.format(self.arg.output_path, p)
            data_out_path = '{}/{}_data.npy'.format(output_path, p)
            label_out_path = '{}/{}_label.pkl'.format(output_path, p)

            if not os.path.exists(output_path):
                os.makedirs(output_path)
            gendata(data_path, label_path, data_out_path, label_out_path, [self.C,self.T,self.V])
            print("Finish %s, %s" %(data_out_path,label_out_path))


    def _extract_from_bag(self,bag_fname):
        '''
        https://github.com/IntelRealSense/librealsense/issues/4934#issuecomment-537705225
        Extract images, depth map and intrinsic parameters from rosbag.
        Maintain the class attribute _kps_2d_dict,_kps_3d_dict, _intrinsic_dict,
        :param bag_fname: The name of vsi file.
        :param img_path: The path to save extracted images.
        :param depth_path: The path to save extracted depth data.
        :return:
        '''

        frames_poses = []
        fcount, skeleton_count = 0, 0 # count how many frames there are in one vsi file
        miss_flag = False
        # h,w,c = self.arg.image_size
        # videos = np.empty([1024,h,w,c], dtype = np.uint8)
        # videos = videos.astype(np.uint8)
        imgs = []
        try:
            config = rs.config()
            pipeline = rs.pipeline()

            # make it so the stream does not continue looping
            config.enable_stream(rs.stream.color)
            config.enable_stream(rs.stream.depth)

            rs.config.enable_device_from_file(config, bag_fname, repeat_playback=False)
            profile = pipeline.start(config)
            depth_sensor = profile.get_device().first_depth_sensor()
            depth_scale = depth_sensor.get_depth_scale()
            # this makes it so no frames are dropped while writing video
            playback = profile.get_device().as_playback()
            playback.set_real_time(False)

            colorizer = rs.colorizer()

            # flag = True

            while True:
                # when stream is finished, RuntimeError is raised, hence this
                # exception block to capture this
                align_to = rs.stream.color
                align = rs.align(align_to)

                frame_present, frames = pipeline.try_wait_for_frames()

                # End loop once video finishes
                if not frame_present:
                    pipeline.stop() # make sure for one pipeline.start() only call pipeline.stop() once, or you will have access violation.
                    break

                # align the depth to color frame
                aligned_frames = align.process(frames)

                # get aligned frames
                aligned_depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()

                # generate image name
                color_fname = generate_imgName(extract_fname(bag_fname), fcount)

                # get depth intrinsic parameters
                prof = aligned_depth_frame.get_profile().as_video_stream_profile()
                intrinsic = prof.get_intrinsics()

                # validate that both frames are valid
                if not aligned_depth_frame or not color_frame:
                    continue

                # generate color image
                color_image_array = np.asanyarray(color_frame.get_data())  # seems the data got directly are BGR
                # # convert color image to BGR for OpenCV
                color_image = cv2.resize(color_image_array,
                                         tuple(self.arg.image_size[:2]),
                                         interpolation=cv2.INTER_AREA)  # shrink image
                imgs.append(color_image)
                color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)

                # generate depth image
                # depth_image = np.asanyarray(aligned_depth_frame.get_data())
                # depth_colormap = depth_image * depth_scale # the depth scale is measured in meters.
                depth_colormap = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())
                depth_colormap = cv2.resize(depth_colormap, tuple(self.arg.image_size[:2]))  # resize image

                # extract pose and set up kps_dict
                kps_2d,kps_3d = self.extractPose(color_image, aligned_depth_frame, intrinsic)

                if kps_3d is not None:
                    frame_pose_dict = {}
                    skeleton_count += 1
                    frame_pose_dict['frame_index'] = fcount
                    skeletons = []
                    for m in range(kps_3d.shape[0]):
                        pose = kps_3d[m,:,0:3]
                        score = kps_3d[m,:, -1]
                        skeletons.append({"pose": pose.tolist(), "score": score.tolist()})

                    frame_pose_dict['skeleton'] = skeletons

                    frames_poses.append(frame_pose_dict)

                    # show image
                    if self.arg.showFlag:
                        # pass
                        self.showImg(color_image, depth_colormap, kps_2d)

                fcount += 1
                if (skeleton_count > self.arg.miss_thresh):
                    miss_flag = True
                # save image
                if self.arg.saveImgFlag:
                    cv2.imwrite("%s/img/%s" % (self.arg.output_path, color_fname),
                                color_image)
                # if cv2.waitKey(self.arg.delay_cv) == 27:
                if cv2.waitKey(1) == 27:
                    break

            print('Processed frame count', fcount)

        except Exception as ex: # close all the resources when an error happens.
            print('Exception occured while processing one bag file: "{}"'.format(ex))

        finally:
            cv2.destroyAllWindows()
            # self._extractor.clean() # clear the pre-declared memory and renew it.

        # self._videos_info_dict[bag_name]["fcount"] = fcount
        #
        # self._videos_info_dict[bag_name]["intrinsic"] = \
        #     {"pp":[intrinsic.ppx,intrinsic.ppy],
        #      'focal': [intrinsic.fx, intrinsic.fy],
        #      "inv. Brown Conrady": intrinsic.coeffs}
        # frame_pose_dict['frame_index'] = frame_index  # save those index only with skeletons in
        # frame_pose_dict['skeleton'] = {"pose": skeletons, 'score': scores}

        video = np.array(imgs).astype(np.uint8)

        return miss_flag, frames_poses, video


