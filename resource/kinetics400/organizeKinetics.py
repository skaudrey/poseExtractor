#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : organizeKinetics.py
@ide    : PyCharm
@time   : 2021-10-25 17:58:56
@descrip: Organize kinetics dataset, make each class folder contain its videos
'''

import argparse
import pandas as pd
import os
# import shutil

def replaceCorrupt(badDir, goodDir):
    cnt = 0
    for i in os.listdir(goodDir):
        tmp_path = "%s/%s"%(badDir,i)
        if os.path.exists(tmp_path):
            # source to the target
            os.replace("%s/%s"%(goodDir,i), "%s/%s"%(badDir,i)) # directly move file, not copy from original folder.
            cnt += 1

    print("Replace %d files in %s" %(cnt, badDir))


def classifyVideos(df, root_dir):
    labels = df['label'].unique()
    for l in labels:
        class_path = "%s/%s"%(root_dir,l) # target path
        vlist = df['youtube_id'][df['label']==l].tolist() # videos of each class
        print("Class %s, estimated %d videos" % (l, len(vlist)))
        for v in vlist:
            cnt = 0
            v_name = "%s_%06d_%06d.mp4"%(v,df[df['youtube_id']==v]['time_start'],df[df['youtube_id']==v]['time_end'])
            tmp_path = "%s/%s"%(root_dir,v_name) # source path
            if os.path.exists(tmp_path):
                # source to the target
                os.replace(tmp_path, "%s/%s"%(class_path,v_name))
                cnt += 1
        print("Real moved files: %d" % cnt)


def buildFolders(root_dir, labels):
    # For each class, new a folder.
    for l in labels:
        tmp_path = "%s/%s"%(root_dir,l)
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)


def main(args):
    # step 1: replace corrupted files
    corrupt_dir = args.corrupt
    replaceCorrupt(args.dir,corrupt_dir)

    # step 2: classify videos into classes
    # step 2.1 read classes and each video's label
    if args.classify:
        df = pd.read_csv(args.annot)
        # step 2.2 create folders
        buildFolders(args.dir,df['label'].unique())
        # step 2.3 classify videos
        classifyVideos(df,args.dir)
    print('Done')

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Organize kinetics files')
    parser.add_argument('-a', '--annot', metavar='DIR',default="./kinetics400/kinetics-400_train.csv ",
                        help='path to annotation files')
    parser.add_argument('-d', '--dir', metavar='DIR', default='./kinetics400/train',
                        help='The directory of videos')

    parser.add_argument('-c', '--corrupt', metavar='DIR', default='./kinetics400/corrupt',
                        help='The directory of videos')

    parser.add_argument('-cls', '--classify', type=bool, default=False,
                            help="Whether to put videos into its label directory.")

    args = parser.parse_args()
    main(args)
