# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:45:44 2019

@author: Michael


@ Modified CMH 2019.12.06
"""


import numpy as np
import cv2

class CVROIGrabber:
    

    def __init__(self, img):
        self.img = img
        self.exit = False
        self.start = None
        self.end = None
        self.roi = None

    def grab(self):
        print('Contrast (std)', np.std(self.img))

        img = np.asarray(self.img / self.img.max(), dtype=float)

        cv2.namedWindow('real image')

        cv2.setMouseCallback('real image', self, 0)

        print("Im at 1")

        while not self.exit:
            print("Im at 2")
            cv2.imshow('real image', img)
            if (cv2.waitKey(0) & 0xFF) == ord('q'):
                cv2.waitKey(1)
                cv2.destroyAllWindows()
                break
        cv2.waitKey(2)

    def __call__(self, event, x, y, flags, params):
        img = self.img
        if event == cv2.EVENT_LBUTTONDOWN:
            print('Start Mouse Position: ' + str(x) + ', ' + str(y))
            print("Im at 3")
            self.start = np.asarray([x, y])

        elif event == cv2.EVENT_LBUTTONUP:
            print("Im at 4")
            self.end = np.asarray([x, y])
            x = np.vstack((self.start, self.end))
            tmp = np.hstack((x.min(axis=0), x.max(axis=0)))
            roi = np.asarray([[tmp[1], tmp[3]], [tmp[0], tmp[2]]], dtype=int) + 1
            print(roi)
            crop = img[roi[0, 0]:roi[0, 1], roi[1, 0]:roi[1, 1]]
            crop = np.asarray(crop / crop.max(), dtype=float)
            self.roi = roi
            cv2.imshow('crop', crop)
            print("Im at 5")
            return self
            
            if (cv2.waitKey(0) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                self.exit = True
                return self