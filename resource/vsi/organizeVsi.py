#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : organizeVsi.py
@ide    : PyCharm
@time   : 2021-11-18 10:21:15
@descrip: To split data into train and val
'''
import argparse
import os
import pandas as pd
import numpy as np
import time
import random
import stat
import shutil


def _generateFakeData(data_path):
    # generate timestamp
    a1 = (2021, 1, 1, 0, 0, 0, 0, 0, 0)  # set start date tuple 1976-01-01 00：00：00）
    a2 = (2021, 6, 30, 23, 59, 59, 0, 0, 0)  # set end date tuple（1990-12-31 23：59：59）
    start = time.mktime(a1)
    end = time.mktime(a2)

    # randomly generate date
    for p in range(2):
        for s in range(20):
            if p == 0 and s >= 10:  # for p1, only 1-10 scenarios. but for p2, 1-20 scenarios
                break
            for r in range(5):
                for e in range(2):
                    t = random.randint(start, end)
                    date_touple = time.localtime(t)  # to time tuple
                    length = random.randint(10,30)
                    bag_id = time.strftime("%Y%m%d_%H%M", date_touple)  # 将时间元组转成格式化字符串（1976-05-21）
                    bag_id += "%d_p%ds%dr%de%d.bag"%(length,p+1,s+1,r+1,e+1)
                    with open("%s/%s"%(data_path,bag_id),'w') as f:
                        f.write("snidenregrneige")

def extractInfo(bagFName):
    '''
    The files have names similar to this: `20210327_115917_p2s11r1e2.vsi`, among which, `20210327` represents the
    acquisition date March 27, 2021, `115917` represents the time 11:59 and lasts for 17 seconds, `p2s11r1e2`
    represents phase 2 scenario 11 repetition 1 student 2.
    :param bagFName:
    :return:
    '''
    tmp = bagFName.split("_")

    bag_fid = tmp[0] + "_" + tmp[1]

    length = tmp[1][-2:]

    phase = int(tmp[2][tmp[2].find("p") + 1:tmp[2].find("s")])

    scenario = int(tmp[2][tmp[2].find("s") + 1:tmp[2].find("r")])  # action label

    repeat = int(tmp[2][tmp[2].find("r") + 1:tmp[2].find("e")])

    subject = int(tmp[2][tmp[2].find("e") + 1:tmp[2].find(".")])

    return bag_fid, phase, scenario, subject,length,repeat

def splitDataset(data_path,out_folder,split_df):
    '''
    iterate split_df and move file according to split value
    :param data_path:
    :param out_folder:
    :param split_df: The predefined dataframe, according to split criterion.
    :return:
    '''
    for index, aitem in split_df.iterrows():
        part = aitem.split
        bag_name = aitem.bag_name
        src,dst = "%s/%s.bag" % (data_path,bag_name),"%s/%s" % (out_folder,part)
        if os.path.exists("%s/%s.bag" % (data_path,bag_name)):
            # source to the target
            os.chmod(src, stat.S_IWRITE)
            shutil.move(src,dst)
            # os.replace()

def labelDataset(criterion, data_path,num_train):
    df = pd.DataFrame(data=None, columns=['bag_name','label','label_anomaly','bag_id','split','length','subject','repeat_id'])

    for filename in os.listdir(data_path):
        if filename.endswith('.bag'):
            bag_fid, phase, scenario, subject, length, repeat_id = extractInfo(filename)
            tmp_dict = {
                'bag_name': filename.split('.')[0],
                'label': scenario,
                'label_anomaly': phase,
                'bag_id': bag_fid,
                'length': length,
                'subject': subject,
                'repeat_id': repeat_id,
                'split':'train'}
            df = df.append(tmp_dict, ignore_index=True)

    if criterion == "xsub":
        df['split'][df['subject'].isin(test_id)] = 'test'
    elif criterion=='xrand':
        train_bag_id = []

        for p in range(2):
            for s in range(20):
                if p==0 and s>=10: # for p1, only 1-10 scenarios. but for p2, 1-20 scenarios
                    break
                for r in range(5):
                    train_bag_id.append("p%ds%dr%de" % (p + 1, s + 1, r + 1))
        random_test_subject = (np.random.randint(2,size=len(train_bag_id))+1).tolist()

        bag_rand_name = list(map(lambda x, y: x + str(y), train_bag_id, random_test_subject))
        # bag_rand_name = list(map(str.__add__, train_bag_id, random_test_subject))
        df['bag_tmp'] = df.bag_name.str.split("_", expand = True).iloc[:,-1]

        df['split'][(df['bag_tmp']).isin(bag_rand_name) ] = 'test'
        df = df.drop('bag_tmp',axis=1)

    df[df['split']=='train'].to_csv("%s/train.csv"%arg.out_folder,index=False)
    df[df['split'] == 'test'].to_csv("%s/test.csv" % arg.out_folder,index = False)

    return df

if __name__ == '__main__':
    # "D:/code/python/st-gcn/"
    parser = argparse.ArgumentParser(
        description='VSI Data Splitter.')
    parser.add_argument(
        '--data_path', default='F:/vsi') # '../../input/vsi/fake'
    parser.add_argument(
        '--out_folder', default='F:/vsi') # '../../input/vsi/fake'
    parser.add_argument(
        '--criterion', default='xsub',type=str,
        help="way to split dataset, candidates are ['xsub','xrand'], "+\
             "which are cross subject (action, cross subject of anomaly), random subject (action, random subject of anomaly)")

    parser.add_argument( '--fake', type=bool, default=False,
                        help="Whether to generate fake data to test")

    arg = parser.parse_args()

    # uncomment and generate fake files if you don't have files currently.
    if arg.fake:
        _generateFakeData(arg.data_path)

    part = ['train', 'test']
    train_id = [1]
    test_id = [2]

    bag_count = len(os.listdir(arg.data_path))
    num_train = int(bag_count/3*2)

    os.chmod(arg.out_folder, stat.S_IWRITE)
    arg.out_folder = arg.out_folder + "/" + arg.criterion
    # os.chmod(arg.out_folder , stat.S_IWRITE)
    if not os.path.exists(arg.out_folder):
        os.mkdir(arg.out_folder)
        os.chmod(arg.out_folder, stat.S_IWRITE)
    for p in part:
        if not os.path.exists(arg.out_folder+"/"+p):
            os.mkdir(arg.out_folder+"/"+p)
            os.chmod(arg.out_folder+"/"+p, stat.S_IWRITE)


    df = labelDataset(arg.criterion, arg.data_path,num_train)

    splitDataset(arg.data_path,arg.out_folder,df)

