#!/usr/bin/python3

from __future__ import print_function, division
import os
import numpy as np
import cv2

__author__ = 'Ben Lai'
__email__ = "laichunpongben@gmail.com"

class TemplateMatcher(object):
    '''
    Apply template matching with OpenCV and
    output the top-left corner coordinates.
    If no match, return (None, None).
    '''

    def __init__(self, template_path, images_folder_path):
        self.template_path = template_path
        self.images_folder_path = images_folder_path
        self.template = cv2.imread(self.template_path, cv2.IMREAD_GRAYSCALE)

    def match(self, image_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        corr = cv2.matchTemplate(self.template, image, cv2.TM_CCOEFF_NORMED)
        return np.unravel_index(corr.argmax(), corr.shape)

    def match_all(self):
        image_paths = [os.path.join(self.images_folder_path, p)
                       for p in sorted(os.listdir(self.images_folder_path))]

        for path in image_paths:
            id_ = path[-7:-4]
            y, x = self.match(path)
            if x and y:
                print('{0},{1},{2}'.format(x, y, id_))
            else:
                print('None,None,{0}'.format(id_))

if __name__ == '__main__':
    import time

    start = time.time()

    template_path = 'q4/large.png'
    images_folder_path = 'q4/small/'
    template_matcher = TemplateMatcher(template_path, images_folder_path)
    print('Start matching...')
    template_matcher.match_all()

    end = time.time()
    lapsed_sec = end - start
    print('Lapsed sec: {0}'.format(lapsed_sec))
