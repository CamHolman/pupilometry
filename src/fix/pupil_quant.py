from CVROIGrabber import CVROIGrabber
from PupilTracker import PupilTracker
import cv2, scipy.io, os, numpy as np

 """
 Author @CMH
 Derived from @MR
 Function to collect pupil quant data
 """ 

# Set Default Params for pupil tracking
#     - can be replaced in function arg
default_params = dict(
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

def pupil_quant_cmh(avi_path, param = default_params, return_clob = False):  
    file_name = os.path.basename(avi_path)[:-4]  
    
    print("Params are:", param)
    print("Filename is:", file_name)
    print("File path is:", avi_path)
    
    #define pupil area
    cap = cv2.VideoCapture(avi_path) #avi_path is the video being called
    cap.set(1,1) #Take the first frame
    ret, frame = cap.read() # Read the frame
    cv = CVROIGrabber(frame)
    cv.grab() # you can drag the window. Q exits

    tr = PupilTracker(param)
    print (cv.roi)

    Pupildata = tr.track(avi_path, cv.roi, display=True)
    
    #save 
    save_path = 'data/interim/'
    cur = save_path + file_name + '_pupilData.npy'
    np.save(cur, Pupildata)
    Pupildata = np.load(cur,allow_pickle=True)
    scipy.io.savemat(save_path + file_name +'_pupilData.mat', {"Pupildata": Pupildata})
    
    if return_clob == True:
        return tr
    
    return 


