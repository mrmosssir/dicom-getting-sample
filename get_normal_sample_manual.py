
# 這個是用來手動取得非骨裂樣本的程式
# 目前被get_sample_auto取代
# 可使用在需額外增加樣本的時候

import cv2
import os
import numpy as np

# in windows10
from tkinter import filedialog
# in macOS
# import Tkinter as Tk
# from tkFileDialog import askopenfilename


def check_folder(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def check_file(path, image):
    count_exist = 1
    path_save = path + 'normal_' + str(count_exist) + '.png'
    while(os.path.isfile(path_save)):
        count_exist = count_exist + 1
        path_save = path + 'normal_' + str(count_exist) + '.png'
    cv2.imwrite(path_save, image)


def get_sample(event, x, y, flags, param):
    global rate_scale
    global image_expend
    sizes = [64, 96, 128]
    path_folder = './normal_extra/'
    check_folder(path_folder)
    if event == cv2.EVENT_LBUTTONUP:
        for size in sizes:
            check_folder(path_folder)
            point_x = int(x * (1 / rate_scale) - size / 2)
            point_y = int(y * (1 / rate_scale) - size / 2)
            image_output = image_expend[point_y: point_y + size, point_x: point_x + size]
            check_file(path_folder, image_output)


def expandImg(imgInput):
    expandArray = np.pad(imgInput, ((256, 256), (256, 256)), "constant", constant_values=(0, 0))
    return expandArray


file_path = filedialog.askopenfilename()
image = cv2.imread(file_path, 0)
image_expend = expandImg(image)

rate_scale = 0.25
rate = (int(image_expend.shape[1] * rate_scale), int(image_expend.shape[0] * rate_scale))
image_scale = cv2.resize(image_expend, rate, cv2.INTER_AREA)

cv2.namedWindow('Preview')
cv2.setMouseCallback('Preview', get_sample)

while (1):
    cv2.imshow('Preview', image_scale)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
