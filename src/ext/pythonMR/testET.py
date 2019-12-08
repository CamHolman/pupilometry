# -*- coding: utf-8 -*-
"""
Created on Mon Jul  8 14:18:30 2019

@author: Michael
"""

    # -*- coding: utf-8 -*-
    #import libraries and define movie
from CVROIGrabber_MRtest import CVROIGrabber
from PupilTracker_MRtest import PupilTracker
import cv2, scipy.io, numpy as np
#from GetAviFiles import avi_path 
    
#avi_path = 'G:/ImagingData/Neuronal_GiDreadd_Astrocyte_CytoGcamp/CNO_1mgKg/20190613_MRAcytoNgi(5)_1mgKg/2x_137um_reg_gcampwLEP_30min_pupilfailaborted'

ext = '.avi'
    
    #define pupil area
cap = cv2.VideoCapture(avi_path+ext) #avi_path is the video being called
cap.set(1,1); #Take the first frame
ret, frame = cap.read() # Read the frame
testframe = CVROIGrabber(frame)
testframe.grab() # you can drag the window. Q exits

#Pupil size tracking
param = dict(
    relative_area_threshold=0.01,#.001
    ratio_threshold=20, #2
    error_threshold=1,
    min_contour_len=5,#5
    margin=0.02,
    contrast_threshold=0.2, #0.2
    speed_threshold=0.2,
    dr_threshold=0.2,#.2
    gaussian_blur=5,#5
    perc_high =90,
    perc_low = 10,
    perc_weight = 0.9,
    )
    
tr = PupilTracker(param)
Pupildata = tr.track(avi_path+ext, testframe.roi, display=True)
    
#save 
np.save('Pupildata.npy',Pupildata)
Pupildata = np.load('Pupildata.npy',allow_pickle=True)
scipy.io.savemat(avi_path+'_pupildata.mat', {"Pupildata":Pupildata})
        

