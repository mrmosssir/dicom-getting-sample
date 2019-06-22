
# 這是用來做資料擴增分類的程式
# 將樣本做 90, 180, 270, 水平及垂直翻轉
# 並將所有樣本分成 train_data 和 validation_data 分別存入資料夾中

import os
from os import listdir

import shutil

import numpy as np
import cv2


def check_folder(path):
    if not (os.path.isdir(path)):
        os.mkdir(path)


def remove_folder(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


def check_files_amount(path):
    for path_folder, name_folder, path_image in os.walk(path):
        return path_image


def process_horizontal(image, path):
    image = np.fliplr(image)
    cv2.imwrite(path, image)


def process_vertical(image, path):
    image = image_vertical = image[::-1]
    cv2.imwrite(path, image)


def process_rotate(image, path):
    global count
    global path_init
    if path.split('/')[1] != path_init:
        count = 1
        path_init = 'validation_data'
    cv2.imwrite(path + str(count) + '.png', image)
    count = count + 1
    process_horizontal(image, path + str(count) + '.png')
    count = count + 1
    process_vertical(image, path + str(count) + '.png')
    count = count + 1
    image_rotate = image
    for index in range(3):
        image_rotate = np.rot90(image_rotate)
        cv2.imwrite(path + str(count) + '.png', image_rotate)
        count = count + 1
        process_horizontal(image_rotate, path + str(count) + '.png')
        count = count + 1
        process_vertical(image_rotate, path + str(count) + '.png')
        count = count + 1
    

def process_image(image_name_array, status):
    global path_init
    path_init = 'train_data'
    if status == '0':
        input_file_name = 'normal'
    elif status == '1':
        input_file_name = 'break'
    for image in range(1, len(image_name_array) + 1):
        image_input = cv2.imread('./' + input_file_name + '/' + input_file_name + '_' + str(image) + '.png')
        if image < int(len(image_name_array) / 6 * 5):
            process_rotate(image_input, './train_data/' + status + '/')
        else:
            process_rotate(image_input, './validation_data/' + status + '/')


def init_folder():
    remove_folder('./train_data')
    remove_folder('./validation_data')
    check_folder('./train_data/')
    check_folder('./train_data/1/')
    check_folder('./train_data/0/')
    check_folder('./validation_data/')
    check_folder('./validation_data/1/')
    check_folder('./validation_data/0/')


path_init = 'train_data'

init_folder()

path_break_image = check_files_amount('./break')
path_normal_image = check_files_amount('./normal')

count = 1
process_image(path_normal_image, '0')

count = 1
process_image(path_break_image, '1')

