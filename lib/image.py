import cv2
import numpy as np
from tqdm import tqdm

def segment_points(img, size=(None, None), ratio=(None, None)):
    img = np.array(img * 255, dtype='uint8')

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    filtered = []
    for cnt in tqdm(contours, desc='Finding Contours: '):
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
    for point in tqdm(filtered, desc='Creating Points: '):
        M = cv2.moments(point['contour'])
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        a = point['area']
        points.append([cY, cX, a])

    print(f'Contours Found: {len(contours)}')
    print(f'Centroids Found: {len(points)}')
    return points