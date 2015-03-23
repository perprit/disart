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
import time

def show1hist(ndarr):
    plt.plot(ndarr)
    plt.show()

def show1image(ndarr):
    #ndarr = cv2.cvtColor(ndarr, cv2.COLOR_BGR2RGB) # TODO
    plt.figure(figsize=(12,8))
    plt.imshow(ndarr, cmap="Greys_r")
    plt.show()

def show2image(ndarr1, ndarr2):
    #ndarr1 = cv2.cvtColor(ndarr1, cv2.COLOR_BGR2RGB) # TODO
    #ndarr2 = cv2.cvtColor(ndarr2, cv2.COLOR_BGR2RGB) # TODO
    plt.figure(figsize=(10,12))
    plt.subplot(211)
    plt.imshow(ndarr1, cmap="Greys_r")
    plt.subplot(212)
    plt.imshow(ndarr2, cmap="Greys_r")
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
    interval = 1
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

    #hue_list = np.array([x for i, x in enumerate(h) if s[i]>5 and v[i]<250]) # TODO comparison operation is too time consuming! 
    hue_list = h[np.where(np.logical_and(s>5, v<250))]

    normal_hue_hist = cv2.calcHist([hue_list], [0], None, [180], [0, 180])
    rescaled_hue_hist = np.array([x**(1/2.)*255/(max(normal_hue_hist)**(1/2.)) for x in normal_hue_hist], dtype=np.uint8)
    th, ret = cv2.threshold(rescaled_hue_hist, 0, 255, cv2.THRESH_OTSU)
    over_th = np.array([x if x>th else 0 for x in rescaled_hue_hist], dtype=np.uint8)
    range_prep = [x != 0 for x in over_th]
    spl = [[x[0] for x in list(y)] for x, y in itertools.groupby(enumerate(range_prep), lambda z: z[1]==False) if not x]
    spl = [[x[0], x[-1]] for x in spl]
    return spl

def areaChartRecog(path, coord=[]):
    start_time = time.time()

    print("%0.5s sec / recognition start" % (time.time() - start_time))

    img = cv2.imread(path, 1)
    width = img.shape[0]
    height = img.shape[1]
    # manipulates chart image
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray_gauss = cv2.GaussianBlur(gray, (13, 13), 0)
    ret, mask = cv2.threshold(gray_gauss, 210, 255, cv2.THRESH_BINARY_INV)
    adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 4)
    
    masked = np.where(mask != 255, 0, 1) # gridline removed

    print("%0.5s sec / image manipulation" % (time.time() - start_time))

    # calculate x-axis histogram to find actual data space
    x_hist = np.sum(masked, axis=0).astype(int)
    x_diff = []
    for i in range(1, len(x_hist)):
        x_diff.append(abs(x_hist[i]-x_hist[i-1]))
    x_gauss = smooth_list_gaussian(x_diff)
    # assume that both left and right limit lines remain
    x_peaks = find_n_peaks(x_gauss, 2)
    #if len(x_peaks) != 2: # TODO
        #print ("WARNING: len(x_peaks) != 2")

    # calculate y-axis histogram to find actual data space
    y_hist = np.sum(masked, axis=1).astype(int)
    y_diff = []
    for i in range(1, len(y_hist)):
        y_diff.append(abs(y_hist[i]-y_hist[i-1]))
    y_gauss = smooth_list_gaussian(y_diff)
    # assume that only the bottom line survives when masked
    y_peaks = find_n_peaks(y_gauss, 1)
    #if len(y_peaks) != 1: # TODO
        #print ("WARNING: len(y_peaks) != 1")

    print("%0.5s sec / identifying peaks" % (time.time() - start_time))

    # extract x-axis ticks data

    x_ticks_margin = {'x': [15, 40], 'y': [-20,20]}
            #x_peaks[0]+x_ticks_margin[2]:x_peaks[1]+x_ticks_margin[3]]
    x_ticks_img = gray[
            np.clip(y_peaks[0]+x_ticks_margin['x'][0], 0, width) : np.clip(y_peaks[0]+x_ticks_margin['x'][1], 0, width),
            np.clip(x_peaks[0]+x_ticks_margin['y'][0], 0, height) : np.clip(x_peaks[1]+x_ticks_margin['y'][1], 0, height)]
    x_ticks_text = pytesseract.image_to_string(Image.fromarray(x_ticks_img)) # TODO

    x_ticks_blur = cv2.GaussianBlur(x_ticks_img, (15,15), 0)
    x_ticks_inv = invert_grayscale(x_ticks_blur)
    x_ticks_hist = np.sum(x_ticks_inv, axis=0)
    x_ticks_gauss = smooth_list_gaussian(x_ticks_hist)
    x_ticks_peaks = find_otsu_peaks(x_ticks_gauss)

    # extract y-axis ticks data

    y_ticks_margin = {'x': [0, 30], 'y': [-50, 0]}
            #x_peaks[0]+y_ticks_margin[2]:x_peaks[0]+y_ticks_margin[3]]
    y_ticks_img = gray[
            np.clip(0+y_ticks_margin['x'][0], 0, width) : np.clip(y_peaks[0]+y_ticks_margin['x'][1], 0, width),
            np.clip(x_peaks[0]+y_ticks_margin['y'][0], 0, height) : np.clip(x_peaks[0]+y_ticks_margin['y'][1], 0, height)]
    y_ticks_text = pytesseract.image_to_string(Image.fromarray(y_ticks_img), config='digits')

    y_ticks_blur = cv2.GaussianBlur(y_ticks_img, (15,15), 0)
    y_ticks_inv = invert_grayscale(y_ticks_blur)
    y_ticks_hist = np.sum(y_ticks_inv, axis=1)
    y_ticks_gauss = smooth_list_gaussian(y_ticks_hist)
    y_ticks_peaks = find_otsu_peaks(y_ticks_gauss)

    x_labels = x_ticks_text.split(' ') # assume that labels in x-axis separated by ' ' # TODO
    y_labels = y_ticks_text.split('\n\n') # assume that labels in y-axis separated by '\n\n' # TODO

    print("%0.5s sec / extracting tick labels" % (time.time() - start_time))

    # contains actual area data
    graph = masked[y_ticks_peaks[0]:y_peaks[0], x_peaks[0]:x_peaks[1]]

    hue_list = hue_ranges(img)
    print("%0.5s sec / hue range" % (time.time() - start_time))
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    y_min = float(y_labels[-1])
    y_max = float(y_labels[0])
    position = []
    value = []

    for hue_range in hue_list:
        area = cv2.inRange(hsv_img, (hue_range[0]-7, 60, 60), (hue_range[1]+7, 255, 255))
        hue_area = area[y_ticks_peaks[0]:y_peaks[0], x_peaks[0]:x_peaks[1]]
        hue_value = []

        for tick in x_ticks_peaks:
            x = tick + x_ticks_margin['y'][0]
            #x = tick - 20
            areaFlag = False
            for y in range(hue_area.shape[0]-1, -1, -1):
                if not areaFlag and hue_area[y][x] != 0:
                    areaFlag = True
                elif areaFlag and (hue_area[y][x] == 0 or y == 0):
                    hue_value.append((y+y_ticks_peaks[0], int(y_max - ((y_max-y_min) * y)/len(hue_area))))
                    break
            if not areaFlag:
                try:
                    hue_value.append(hue_value[-1])
                except IndexError: # len(hue_pos) == 0 or len(hue_value) == 0
                    hue_value.append((0,0))

        for i, p in enumerate(hue_value):
            if p == (0, 0):
                try: # i < len(hue_value)-1
                    hue_value[i] = hue_value[i+1]
                except IndexError: # i == len(hue_value)-1
                    hue_value[i] = hue_value[i-1]

        position.append([int(p[0]) for p in hue_value])
        value.append([int(p[1]) for p in hue_value])
        
    print("%0.5s sec / extract data from graph area" % (time.time() - start_time))

    result = {}
    sample = x_labels
    element = hue_list

    result['sample'] = sample
    result['element'] = element
    result['position'] = position
    result['value'] = value

    result_json = json.dumps(result)

    print result_json
    print("%0.5s sec / execution end" % (time.time() - start_time))
    return result_json

if __name__ == "__main__":
    # load image
    if len(sys.argv) != 2:
        print "Usage: %s <image_filename>" % sys.argv[0]
        raise ReferenceError
    path = sys.argv[1]

    if (path is None) or (len(path) == 0):
        print "ERROR: image '%s' not found" % sys.argv[1]
        raise ReferenceError
    areaChartRecog(path)
