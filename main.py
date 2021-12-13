#!usr/bin/env python
# -*- coding:utf-8 -*-
'''
@author  : Miao
@file   : main.py
@ide    : PyCharm
@time   : 2021-11-17 16:48:53
@descrip: 
'''
import argparse
import sys
from torchlight import import_class

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Processor collection')

    # region register processor yapf: disable
    processors = dict()
    processors['bag'] = import_class('process.BagIterator')
    processors['video'] = import_class('process.VideoIterator')
    # processors['skeleton'] = import_class('process.VideoIterator') # to deal with skeleton

    # add sub-parser
    subparsers = parser.add_subparsers(dest='processor')
    for k, p in processors.items():
        subparsers.add_parser(k, parents=[p.get_parser()])

    # read arguments
    arg = parser.parse_args()

    # start
    Processor = processors[arg.processor]
    p = Processor(sys.argv[2:])

    p.start()

