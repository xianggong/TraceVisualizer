#!/usr/bin/python
""" This module contains misc functions """

import random
import re


def atoi(text):
    """ atoi function """
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split('(\d+)', text)]


def get_random_color():
    """ Get random color """
    return "#%06x" % random.randint(0, 0xFFFFFF)
