# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 14:45:44 2019

@author: Michael
"""
import numpy as np
import cv2

class CVROIGrabber:
    start = None
    end = None
    roi = None

    def __init__(self, img):
        self.img = img
        self.exit = False

    def grab(self):
        print('Contrast (std)', np.std(self.img))
        img = np.asarray(self.img / self.img.max(), dtype=float)
        cv2.namedWindow('real image')
        cv2.setMouseCallback('real image', self, 0)

        while not self.exit:
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
            self.start = np.asarray([x, y])

        elif event == cv2.EVENT_LBUTTONUP:
            self.end = np.asarray([x, y])
            x = np.vstack((self.start, self.end))
            tmp = np.hstack((x.min(axis=0), x.max(axis=0)))
            roi = np.asarray([[tmp[1], tmp[3]], [tmp[0], tmp[2]]], dtype=int) + 1
            print(roi)
            crop = img[roi[0, 0]:roi[0, 1], roi[1, 0]:roi[1, 1]]
            crop = np.asarray(crop / crop.max(), dtype=float)
            self.roi = roi
            cv2.imshow('crop', crop)
            return self
            
            if (cv2.waitKey(0) & 0xFF) == ord('q'):
                cv2.destroyAllWindows()
                self.exit = True
                return self