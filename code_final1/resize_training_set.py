# -*- coding: utf-8 -*-
"""Final_resize training set.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UMvvT14nCyAAjQRwxilTo1su_ztjawp4
"""

import cv2
import os


def resize_training_set_digits(input_path, output_path):
    for filename in os.listdir(input_path):
        image = cv2.imread(filename, 0)  # Read the gray image
        ret, img_bin = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Binarization
        height = img_bin.shape[0]
        length = img_bin.shape[1]

        a = 30 / height  # CNN needs the height of the input image to be 30
        img_resize = cv2.resize(img_bin, (int(length * a), 30), )
        new_path = output_path + filename
        cv2.imwrite(new_path, img_resize)


LOAD_PATH = 'labeled_digits'
SAVE_PATH = 'new_labeled_data/'
resize_training_set_digits(LOAD_PATH, SAVE_PATH)
