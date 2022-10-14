import cv2
import numpy as np
from tqdm import tqdm

def segment_points(img=None, test=True, size=(None, None), ratio=(None, None)):
    print(img.max())
    img = np.array(img * 255, dtype='uint8')
    print(img.max())

    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    total_mask = np.zeros(img.shape, dtype="uint32")

    if test: good_contours = contours
    else:
        good_contours = []
        for i, cnt in enumerate(tqdm(contours, desc='Filtering Contours: ')):
            area = cv2.contourArea(cnt)
            x,y,w,h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h

            if not size[0] == None and area < size[0]: continue
            elif not size[1] == None and area > size[1]: continue
            elif not ratio[0] == None and aspect_ratio < ratio[0]: continue
            elif not ratio[1] == None and aspect_ratio > ratio[1]: continue
            else: good_contours.append(cnt)

    for i, cnt in enumerate(tqdm(good_contours, desc='Creating Visualization: ')):
        mask = np.zeros(img.shape, dtype="uint8")
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        total_mask[mask == 255] = i+1

        area = cv2.contourArea(cnt)
        x,y,w,h = cv2.boundingRect(cnt)
        aspect_ratio = float(w)/h

    if not test:
        points = []
        for i,label in enumerate(tqdm(np.unique(total_mask), desc='Saving Points: ')):
            if label == 0: continue

            mask = np.zeros(img.shape, dtype="uint8")
            mask[total_mask == label] = 255
            cnt, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

            M = cv2.moments(cnt[0])
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            points.append([cY, cX])

    print(f'Contours Found: {len(contours)}')
    print(f'Contours After Filtering: {len(good_contours)}')
    return good_contours, total_mask, points