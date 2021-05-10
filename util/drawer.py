#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : drawer.py
@ide    : PyCharm
@time   : 2021-05-04 09:47:11
@descrip: 
'''

class SkeletonDrawer():
    def __init__(self):
        self._skeltons_lines = {
            "OPENPOSE":[ # https://user-images.githubusercontent.com/9403813/87262012-6d802d80-c486-11ea-9629-107e09d5c255.png
                [17, 15, 0, 1, 8, 9, 10, 11, 22, 23],  # Right eye down to right leg
                [11, 24],  # Right heel
                [18, 16, 0],  # Left eye
                [4, 3, 2, 1, 5, 6, 7],  # Arms
                [8, 12, 13, 14, 19, 20],  # Left leg
                [14, 21]  # Left heel
            ],
            "CUBEMOS":[ #https://miao-picbed-1305768714.cos.ap-shanghai.myqcloud.com/img/image-20210510121456746.png
                [16, 14, 0, 1, 8, 9, 10],  # Right eye down to right leg
                [17, 15, 0],  # Left eye
                [4, 3, 2, 1, 5, 6, 7],  # Arms
                [1, 11, 12, 13],  # Left leg
            ]
        }

    def drawSkeleton(self,model_type):

        if model_type not in ["OPENPOSE","CUBEMOS","NUITRACK"]:
            print("Please set an acceptable skeleton model")
            exit(-1)



        return self._skeltons_lines[model_type]
