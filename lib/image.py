import cv2
import numpy as np
from tqdm import tqdm

from lib.utils import Color

def segment_points(img, size=(None, None), ratio=(None, None)):
    clr = Color()

    img = np.array(img * 255, dtype='uint8')

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    filtered = []
    for cnt in tqdm(contours, desc=f'{clr.GREY}Finding Contours: ', postfix=clr.ENDC):
        area = cv2.contourArea(cnt)
        if area == 0: continue
        x,y,w,h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h

        if not size[0] == None and area < size[0]: continue
        elif not size[1] == None and area > size[1]: continue
        elif not ratio[0] == None and aspect_ratio < ratio[0]: continue
        elif not ratio[1] == None and aspect_ratio > ratio[1]: continue
        else: filtered.append({'contour': cnt, 'area': area})

    points = []
    for point in tqdm(filtered, desc=f'{clr.GREY}Creating Points: ', postfix=clr.ENDC):
        M = cv2.moments(point['contour'])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        a = point['area']
        points.append([cY, cX, a])

    print(f'{clr.GREY}Contours Found: {len(contours)}{clr.ENDC}')
    print(f'{clr.GREY}Centroids Found: {len(points)}{clr.ENDC}')
    return points