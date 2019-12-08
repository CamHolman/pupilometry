# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 19:09:44 2019

@author: Michael
"""

import os
import Pupil_Quant_MR
ext = '.avi'
for root, dirs, files in os.walk("G:/ImagingData/Neuronal_GiDreadd_Neuronal_Gcamp6f"):
    for file in files:
        if (file.endswith(ext) and not "BAD" in file) is True:
            avi_path = os.path.join(root, file)
            matcheck = avi_path.replace('.avi','_pupildata.mat')
            avi_path = avi_path.replace('.avi','')
            if os.path.exists(matcheck) is False:
                print ("analyzing", avi_path)
                Pupil_Quant_MR.Pupil_Quant_MR()
print("Finished!")

