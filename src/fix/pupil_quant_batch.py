import os
import skimage as sk
from src.fix.pupil_quant import pupil_quant_cmh

"""
Author CMH
Function to collect batch data for pupil quant
"""

def pupil_quant_batch(input_dir, output_dir = None):
    images = sk.io.ImageCollection(os.path.join(input_dir, '*.avi'))
    # print (images.files)

    vid_list = [] 

    for i in range(len(images.files)):
        print ('Current Index in Batch Function =', i)

        image_path = images.files[i]
        image_name = os.path.basename(image_path)[:-4]

        cur_clob =  pupil_quant_cmh(image_path, return_clob = True)
        
        if output_dir != None:
            sk.external.tifffile.imsave(output_dir + image_name + ".tif", pp_image, 'imagej')
        
        vid_list.append([cur_clob])

    return vid_list