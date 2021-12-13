#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : pathUtil.py
@ide    : PyCharm
@time   : 2021-05-01 21:23:32
@descrip: Deal the path stuff, like extract filename without suffix.
'''
import pickle as pkl
def extract_fname(aPath):
    tmp = aPath.split("/")[-1]
    fname = tmp.split('.')[0]

    return fname

def generate_imgName(bag_name,f_index):
    '''
    The image name that extracted from each vsi file. It's named as <bag_name>_frame_<f_index>
    :param bag_name: The name of vsi file
    :param f_index: frame index
    :return:
    '''
    fname = "frame_{:06d}".format(f_index) + ".png"
    img_name = "%s_%s" % (bag_name, fname)
    return img_name

def saveDataAsPkl(data,filename):
    with open(filename, 'wb') as f:
        pkl.dump(data, f)

def saveData(data,filename):
    if filename.endswith(".pkl"):
        saveDataAsPkl(data,filename)
    elif filename.endswith(".txt"):
        with open(filename,'w') as f:
            f.write('\n'.join(str(a) for a in data))

