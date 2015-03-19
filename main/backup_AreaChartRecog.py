#!/usr/bin/python

import sys
import cv2
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import itertools
import pytesseract
import Image
import simplejson as json

def show1hist(ndarr):
    plt.plot(ndarr)
    plt.show()

def show1image(ndarr):
    plt.figure(figsize=(12,8))
    plt.imshow(ndarr, cmap="Greys_r")
    plt.show()

def invert_grayscale(img):
    inv = 255 - img
    return inv

# smoothing 1-dimension list with gaussian method
# http://www.swharden.com/blog/2008-11-17-linear-data-smoothing-in-python/
def smooth_list_gaussian(li, strippedXs=False, degree=5):
    window = degree*2-1
    weight = np.array([1.0]*window)
    weightGauss = []
    for i in range(window):
        i = i-degree+1
        frac=i/float(window)
        gauss=1/(np.exp((4*(frac))**2))
        weightGauss.append(gauss)
    weight = np.array(weightGauss) * weight
    smoothed = [0.0]*(len(li)-window)
    for i in range(len(smoothed)):
        smoothed[i] = sum(np.array(li[i:i+window])*weight)/sum(weight)
    return smoothed

# find exactly N-highest peaks
def find_n_peaks(hist, n):
    interval = (int) ((max(hist) - min(hist)) / 1000);
    for walker in range(int(max(hist)), int(min(hist)), -interval):
        cnt = 0
        encounter = []
        for i in range(1, len(hist)):
            if (hist[i-1] < walker and walker < hist[i]) or (hist[i-1] > walker and walker > hist[i]):
                cnt += 1
                encounter.append(i-1)
        if cnt >= n * 2:
            return [(encounter[i]+encounter[i+1])/2 for i in range(0, len(encounter), 2)]
    return [] # error case

# find peaks using otsu threshold
def find_otsu_peaks(hist):
    rescaled = np.array([x**(1/2.)*255/(max(hist)**(1/2.)) for x in hist], dtype=np.uint8)
    th, ret = cv2.threshold(rescaled, 0, 255, cv2.THRESH_OTSU)
    over_th = np.array([x if x>th else 0 for x in rescaled], dtype=np.uint8)
    range_prep = [x != 0 for x in over_th]
    spl = [[x[0] for x in list(y)] for x, y in itertools.groupby(enumerate(range_prep), lambda z: z[1]==False) if not x]
    spl = [(x[0]+x[-1])/2 for x in spl]
    return spl

# get hue ranges from image using otsu threshold
def hue_ranges(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h = hsv_img[:, :, 0].flatten()
    s = hsv_img[:, :, 1].flatten()
    v = hsv_img[:, :, 2].flatten()
    hue_list = np.array([x for i, x in enumerate(h) if s[i]>5 and v[i]<250])
    normal_hue_hist = cv2.calcHist([hue_list], [0], None, [180], [0, 180])
    rescaled_hue_hist = np.array([x**(1/2.)*255/(max(normal_hue_hist)**(1/2.)) for x in normal_hue_hist], dtype=np.uint8)
    th, ret = cv2.threshold(rescaled_hue_hist, 0, 255, cv2.THRESH_OTSU)
    over_th = np.array([x if x>th else 0 for x in rescaled_hue_hist], dtype=np.uint8)
    range_prep = [x != 0 for x in over_th]
    spl = [[x[0] for x in list(y)] for x, y in itertools.groupby(enumerate(range_prep), lambda z: z[1]==False) if not x]
    spl = [[x[0], x[-1]] for x in spl]
    return spl

def get_histogram(img):
    # manipulates chart image
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray_gauss = cv2.GaussianBlur(gray, (13, 13), 0)
    ret, mask = cv2.threshold(gray_gauss, 210, 255, cv2.THRESH_BINARY_INV)
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 4)

    masked = np.where(mask != 255, 0, adaptive) # gridline removed

    # calculate x-axis histogram to find actual data space
    x_hist = np.sum(masked, axis=0).astype(int)
    x_diff = []
    for i in range(1, len(x_hist)):
        x_diff.append(abs(x_hist[i]-x_hist[i-1]))
    x_gauss = smooth_list_gaussian(x_diff)
    ## assume that both left and right limit lines remain

    # calculate y-axis histogram to find actual data space
    y_hist = np.sum(masked, axis=1).astype(int)
    y_diff = []
    for i in range(1, len(y_hist)):
        y_diff.append(abs(y_hist[i]-y_hist[i-1]))
    y_gauss = smooth_list_gaussian(y_diff)
    ## assume that only the bottom line survives when masked
    
    return {'x_hist': x_gauss, 'y_hist': y_gauss}

#def main():
    #graph = adaptive[y_peaks[0]:y_peaks[-1], x_peaks[0]:x_peaks[-1]]
    ## extract x-axis ticks data

    #x_ticks_img = gray[y_peaks[-1]+10:len(img)-30, x_peaks[0]-20:x_peaks[-1]+20]
    #x_ticks_text = pytesseract.image_to_string(Image.fromarray(x_ticks_img)) # TODO

    #x_ticks_blur = cv2.GaussianBlur(x_ticks_img, (15,15), 0)
    #x_ticks_inv = invert_grayscale(x_ticks_blur)
    #x_ticks_hist = np.sum(x_ticks_inv, axis=0)
    #x_ticks_gauss = smooth_list_gaussian(x_ticks_hist)
    #x_ticks_peaks = find_otsu_peaks(x_ticks_gauss)

    ## extract y-axis ticks data

    #y_ticks_img = gray[y_peaks[0]-10:y_peaks[-1]+10, 0+30:x_peaks[0]-10]
    #y_ticks_text = pytesseract.image_to_string(Image.fromarray(y_ticks_img), config='digits')

    #y_ticks_blur = cv2.GaussianBlur(y_ticks_img, (15,15), 0)
    #y_ticks_inv = invert_grayscale(y_ticks_blur)
    #y_ticks_hist = np.sum(y_ticks_inv, axis=1)
    #y_ticks_gauss = smooth_list_gaussian(y_ticks_hist)
    #y_ticks_peaks = find_otsu_peaks(y_ticks_gauss)

    #x_labels = x_ticks_text.split(' ') # assume that labels in x-axis separated by ' ' # TODO
    #y_labels = y_ticks_text.split('\n\n') # assume that labels in y-axis separated by '\n\n' # TODO

    ## contains actual area data
    ##graph = masked[y_ticks_peaks[0]:y_peaks[0], x_peaks[0]:x_peaks[1]]

    #hue_list = hue_ranges(img)
    #hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #y_min = float(y_labels[-1])
    #y_max = float(y_labels[0])
    #position = []
    #value = []

    #for hue_range in hue_list:
        #area = cv2.inRange(hsv_img, (hue_range[0]-7, 60, 60), (hue_range[1]+7, 255, 255))
        ##hue_area = area[y_ticks_peaks[0]:y_peaks[0], x_peaks[0]:x_peaks[1]]
        #hue_area = area[y_peaks[0]:y_peaks[-1], x_peaks[0]:x_peaks[-1]]
        #hue_pos = []
        #hue_value = []

        #for tick in x_ticks_peaks:
            #x = tick - 20
            #areaFlag = False
            #for y in range(hue_area.shape[0]-1, -1, -1):
                #if not areaFlag and hue_area[y][x] != 0:
                    #areaFlag = True
                #elif areaFlag and (hue_area[y][x] == 0 or y == 0):
                    #hue_pos.append(y+y_ticks_peaks[0])
                    #hue_value.append(int(y_max - ((y_max-y_min) * y)/len(hue_area)))
                    #break

        #position.append(hue_pos)
        #value.append(hue_value)

    #result = {}
    #sample = x_labels
    #element = hue_list

    #result['sample'] = sample
    #result['element'] = element
    #result['position'] = position
    #result['value'] = value

    #result_json = json.dumps(result)

    #print result_json

