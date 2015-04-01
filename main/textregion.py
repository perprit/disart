#!/usr/bin/python

import sys
import cv2
import matplotlib.pyplot as plt
import numpy as np

def show1image(ndarr):
    #ndarr = cv2.cvtColor(ndarr, cv2.COLOR_BGR2RGB) # TODO
    plt.figure(figsize=(12,8))
    plt.imshow(ndarr, cmap="Greys_r")
    plt.show()

# load image
if len(sys.argv) != 2:
    print "Usage: %s <image_filename>" % sys.argv[0]
    raise ReferenceError
path = sys.argv[1]
large = cv2.imread(path)
#rgb = cv2.pyrDown(large)
rgb = large
small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, morphKernel)
th, bw = cv2.threshold(grad, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

mask = np.zeros(bw.shape, np.uint8)
morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (6, 4))
connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, morphKernel)
show1image(connected)
temp, contours, hierarchy = cv2.findContours(connected, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

rect_width_sum = 0
rect_cnt = 0

idx = 0
while idx >= 0:
    rect = cv2.boundingRect(contours[idx])
    rect_x = rect[0]
    rect_y = rect[1]
    rect_width = rect[2]
    rect_height = rect[3]
    cv2.drawContours(mask, contours, idx, (255, 255, 255), cv2.FILLED)
    maskROI = mask[rect_y:rect_y+rect_height, rect_x:rect_x+rect_width]
    r = float(cv2.countNonZero(maskROI))/(rect_width * rect_height)

    if r>0.45 and (rect_width > 4 and rect_height > 4):
        cv2.rectangle(rgb, (rect_x, rect_y), (rect_x+rect_width, rect_y+rect_height), (0, 255, 0))
        rect_width_sum += rect_width
        rect_cnt += 1

    idx = hierarchy[0][idx][0]

rect_width_sum /= rect_cnt
print "rect_width_average = " + str(rect_cnt)
show1image(rgb)
