# -*- coding: utf-8 -*-
"""
Useful functions for modifying image files for display on mono LCD screens

@author: Andrew
"""

# You need the OpenCV and numpy python libraries installed
import cv2
import numpy

# Compress image for feeding to monochrome LCD screen
def Image_squash(image_in):
    
    # Get image shape
    image_y, image_x = image_in.shape
    
    # Make empty image of final shape
    image_out = numpy.zeros((image_y,int(image_x/3),3))
    
    # Compress width of image into colour space
    # For every three x-axis pixels, compress them into a single colour
    for y in range(0,image_y):
        for x in range(0,int(image_x/3)):
            image_out[y,x,0] = image_in[y,(x*3)+2]
            image_out[y,x,1] = image_in[y,(x*3)+1]
            image_out[y,x,2] = image_in[y,(x*3)]
    
    return image_out

# Apply flat field correction to compensate for LED non-uniformity
def FFC(image_in, image_vig, FFC_strength):
    
    image_vig = cv2.medianBlur(image_vig, 15)  # Apply median filter for removing artifacts and extreme pixels.
    vig_adjusted = cv2.convertScaleAbs(image_vig,1,1.5) # Adjust vignette brightness and contrast if needed

    vig_norm = vig_adjusted.astype(numpy.float32) / 255  # Convert vig to float32 in range [0, 1]
    vig_norm = cv2.GaussianBlur(vig_norm, (51, 51), 30)  # Blur the vignette template to make it smoother
    vig_mean_val = cv2.mean(vig_norm)[0]
    inv_vig_norm = vig_mean_val / vig_norm  # Compute G = m/F

    image_FFC = cv2.multiply(image_in, inv_vig_norm, dtype=cv2.CV_8U)  # Compute: C = R * G
    image_out = cv2.addWeighted(image_FFC, FFC_strength, image_in, 1 - FFC_strength, 0.0) # Blend together the original and corrected images if desired
    return image_out

# Pad image to fill LCD screen if it's not large enough
def Pad_image(image,full_x,full_y,border):
    
    # Get image shape and bit depth
    image_y, image_x = image.shape
    depth = image.dtype
    
    # What the border gets filled in as depends on what is desired and also bit depth
    if border == "Black":
        edge_value = 0 # Black is always 0
    else:
        if depth == 'uint16':
            edge_value = 65535 # White if the image is 16-bit
        else:
            edge_value = 255 # White if the image is 8-bit
    
    # Calculate required border if any to fill LCD with the image in the middle
    dx = int((full_x - image_x)/2)
    dy = int((full_y - image_y)/2)
    dx_remainder = full_x - (2*dx+image_x)
    dy_remainder = full_y - (2*dy+image_y)
    
    # Create the padded image
    image_padded = cv2.copyMakeBorder(image,dy,dy+dy_remainder,dx,dx+dx_remainder,cv2.BORDER_CONSTANT,value=[edge_value,edge_value,edge_value])
    
    return image_padded