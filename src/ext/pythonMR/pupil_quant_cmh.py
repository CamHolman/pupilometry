def pupil_quant_cmh(avi_path):

    # -*- coding: utf-8 -*-
    #import libraries and define movie
    from CVROIGrabber_MRtest import CVROIGrabber
    from src.ext.PupilTracker_MRtest import PupilTracker
    import cv2, scipy.io, numpy as np

    
    
    
    
    
    #define pupil area
    cap = cv2.VideoCapture(avi_path) #avi_path is the video being called
    cap.set(1,1); #Take the first frame
    ret, frame = cap.read() # Read the frame
    cv = CVROIGrabber(frame)
    cv.grab() # you can drag the window. Q exits
    
    
    #Pupil size tracking parameters (why are these in a function)
    param = dict(
    relative_area_threshold=0.01,#.001
    ratio_threshold=2, #2
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
    Pupildata = tr.track(avi_path, cv.roi, display=True)
    
    #save 
    np.save('Pupildata.npy',Pupildata)
    Pupildata = np.load('Pupildata.npy',allow_pickle=True)
    scipy.io.savemat(avi_path[:-4]+'_pupildata.mat', {"Pupildata": Pupildata})
        
    return

