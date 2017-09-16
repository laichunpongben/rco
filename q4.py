#!/usr/bin/python3

from __future__ import print_function, division
import os
import numpy as np
from scipy import signal, misc
import cv2

__author__ = 'Ben Lai'
__email__ = "laichunpongben@gmail.com"

class PixelMatcher(object):
    def __init__(self, large_image_path, small_images_folder_path):
        self.large_image_path = large_image_path
        self.small_images_folder_path = small_images_folder_path
        self.large_image = cv2.imread(self.large_image_path, cv2.IMREAD_GRAYSCALE) / 255

    def match(self, image_path):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE) / 255
        corr = signal.correlate2d(self.large_image, image, boundary='symm', mode='same')
        return np.unravel_index(np.argmax(corr), corr.shape)

    def match_all(self):
        small_image_paths = [os.path.join(self.small_images_folder_path, p)
                             for p in sorted(os.listdir(self.small_images_folder_path))]

        for path in small_image_paths:
            id_ = path[-7:-4]
            y, x = self.match(path)
            if x and y:
                print('{0},{1},{2}'.format(y, x, id_))
            else:
                print('None,None,{0}'.format(id_))

if __name__ == '__main__':
    import time

    start = time.time()

    large_image_path = 'q4/large.png'
    small_images_folder_path = 'q4/small/'
    pixel_matcher = PixelMatcher(large_image_path, small_images_folder_path)
    pixel_matcher.match_all()

    end = time.time()
    lapsed_sec = end - start
    print('Lapsed sec: {0}'.format(lapsed_sec))
