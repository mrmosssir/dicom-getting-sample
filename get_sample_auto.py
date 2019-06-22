
# 主要的樣本擷取程式

import os
from os import listdir

import random
import shutil
import argparse

import pydicom
import numpy as np
import cv2

# in windows10
from tkinter import filedialog
# in macOS
# import Tkinter as Tk
# from tkFileDialog import askdirectory


# args setting
parser = argparse.ArgumentParser(description='Get the training sasmple', 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('--amount', '-a', type=int, default=10, help='Break sample and Normal sampel ratio.')

args = parser.parse_args()


# 確認截圖範圍有沒有超出圖片
def check_coordinate(point):
    if(point <= 0):
        return 0
    else: 
        return point


# 確認資料夾是否存在
def check_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)


# 移除資料夾
def remove_folder(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


# 資料夾內容初始化
def init_folder():
    remove_folder('./break')
    remove_folder('./normal')
    check_folder('./break')
    check_folder('./normal')


# 切圖的 function
def cut_out(source_image, x_point, y_point, path, mode):
    global break_count
    global normal_count
    sizes = [64, 96, 128]
    for size in sizes:
        if mode == 0:
            normal_count = normal_count + 1
            path_output = path + 'normal_' + str(normal_count) + '.png'
        else:
            break_count = break_count + 1
            path_output = path + 'break_' + str(break_count) + '.png'
        # 座標偏左上
        x = check_coordinate(int(x_point - size / 2))
        y = check_coordinate(int(y_point - size / 2))
        image_output = source_image[y: y + size, x: x + size]
        cv2.imwrite(path_output, image_output)


# 骨裂樣本擷取 獲取 Dicom 座標 -> 擷取樣本 -> 記錄回傳骨裂座標位置
def get_break_sample(dataset_dicom, source_image, image_output_path):
    global break_count
    item_array = []
    for dataset_item in dataset_dicom[0x70, 0x01][0][0x70, 0x09]:
        push_buffer = []
        for item in dataset_item[0x70, 0x22]:
                push_buffer.append(item)
        if len(push_buffer) >= 10:
            point_buffer = np.array([(push_buffer[0] + push_buffer[2]) / 2 + 256, (push_buffer[1] + push_buffer[5]) / 2 + 256])
            item_array.append(point_buffer)
    for dataset_point in item_array:
        cut_out(source_image, dataset_point[0], dataset_point[1], image_output_path, 1)
    return item_array


# 非骨裂樣本擷取 獲取骨裂座標位置 -> 隨機產生座標 -> 確定不在骨裂樣本的範圍內 -> 擷取樣本
def get_normal_sample(break_point_array, source_image, image_output_path):
    sizes = [64, 96, 128]
    sample_amount_magnification = args.amount
    for amount in range(len(break_point_array) * sample_amount_magnification):
        mix_check = False
        rand_x_point, rand_y_point = 0, 0
        while not mix_check:
            mix_check = True
            rand_x_point = random.randint(257, source_image.shape[1] - 256)
            rand_y_point = random.randint(257, source_image.shape[0] - 256)
            for point_scanner in break_point_array:   
                x_range = range(int(point_scanner[0]) - 128, int(point_scanner[0]) + 127)
                y_range = range(int(point_scanner[1]) - 128, int(point_scanner[1]) + 127)
                if (rand_x_point - 128 in x_range or rand_x_point + 127 in x_range) and (rand_y_point - 128 in y_range or rand_y_point + 127 in y_range):
                    mix_check = False
        cut_out(source_image, rand_x_point, rand_y_point, image_output_path, 0)


# 樣本擷取控制 用來控制儲存資料夾及樣本擷取的模式
def get_sample(path_dicom, source_image):
    break_output_folder = './break/'
    normal_output_folder = './normal/'
    dataset_point = np.array([0, 0])
    if not os.path.isfile(path_dicom):
        return 
    dataset = pydicom.dcmread(path_dicom)
    break_point_array = get_break_sample(dataset, source_image, break_output_folder)
    get_normal_sample(break_point_array, source_image, normal_output_folder)
    

# 做一些檔案的初步設定以及原圖的處理 然後啟動樣本擷取
def process_image(path_input):
    folder_list = listdir(path_input)
    folder_source = './source/'
    check_folder(folder_source)
    for index in folder_list:
        if index != ".DS_Store":
            image_dicom = pydicom.read_file(path_input + "/" + index + "/I0000000")
            image_array = image_dicom.pixel_array
            image_scale = cv2.convertScaleAbs(image_array - np.min(image_array), alpha=(255.0 / min(np.max(image_array) - np.min(image_array), 10000)))
            image_expand = np.pad(image_scale, ((256, 256), (256, 256)), 'constant', constant_values=(0, 0))
            cv2.imwrite(folder_source + index + '.png', image_expand)
            path_dicom = path_input + "/" + index + "/I0000001"
            get_sample(path_dicom, image_expand)


init_folder()
break_count, normal_count = 0, 0

path_folder = filedialog.askdirectory()
process_image(path_folder)
print("sample process finish please run data_augmentation.py")

