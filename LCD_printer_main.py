# -*- coding: utf-8 -*-
"""
Simple script to manipulate an image for display on a mono LCD screen for alt-process printing

@author: Andrew
"""

import cv2
import numpy
import os, shutil
import pandas as pd
from LCD_printing_function_library import Image_squash, FFC, Pad_image

# Path to input image, FFC images and adjustment curve
path = "Ancient_stone"
vignette = 'Field correction photos/20240727 - Grey print/Uncorrected_print_1_curved_blur.png'
vignette_2 = 'Field correction photos/20240727 - Grey print/Corrected_print_1_curved_blur.png'
curve_path = "../Cyanotype cals/LCD/Hahnemuhle Harmony/HAHT_LCD_CAL_2.csv"

Apply_FFC = True # Apply flat field correction yes/no
Apply_curve = True # Apply correction curve yes/no
FFC_strength = 1.25 # Adjustable flat field correction strength
border = "Black" # Black or white border (as viewed on the final print)

# Exposure steps for 16-bit images
steps = 1

# LCD screen dimensions
LCD_x = 6480
LCD_y = 3600

# Load image, convert to greyscale if required and read size
image_in = cv2.imread(path+'.png', cv2.IMREAD_UNCHANGED)
if len(image_in.shape) == 3:
    image_gray = cv2.cvtColor(image_in, cv2.COLOR_BGR2GRAY)
else:
    image_gray = image_in
depth = image_in.dtype

# Load FFC correction images
image_vig = cv2.imread(vignette, cv2.IMREAD_GRAYSCALE)
image_vig_2 = cv2.imread(vignette_2, cv2.IMREAD_GRAYSCALE)
    
# Load correction curve LUT
LUT = pd.read_csv(curve_path,header=None).to_numpy()

# Flip image for printing
image_gray = cv2.flip(image_gray,0)

# Pad image with black or white to fill LCD
image_padded = Pad_image(image_gray,LCD_x,LCD_y,border)

# Check to see if output folder exists, if not make it
if os.path.exists('Output'):
    # Delete contents
    for filename in os.listdir('Output'):
        file_path = os.path.join('Output', filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
else:
    # Make output directory
    os.makedirs('Output')

# Check if image is 8 or 16 bit, if it's 16 bit make n exposure steps
if depth == 'uint16':
    # Create n = steps number of images with brightness shifted to give more dynamic range
    for n in range(0,steps):
        image_stepped = image_padded + (n*(256/steps))
        image_stepped = numpy.clip(image_stepped,0,(2**16)-1)
        image_stepped = (image_stepped/256).astype('uint8')

        # Apply correction LUT
        if Apply_curve:
            curved_image = cv2.LUT(image_stepped,LUT).astype('uint8')
        else:
            curved_image = image_stepped
        
        # Invert to negative
        curved_image = cv2.absdiff(curved_image, 255)
        
        if Apply_FFC:
            # Apply flat field correction
            curved_image = FFC(curved_image, image_vig, FFC_strength)
            curved_image = FFC(curved_image, image_vig_2, FFC_strength)
        
        # Squash image for mono LCD
        image_out = Image_squash(curved_image)
        
        # Save to folder
        cv2.imwrite('Output/'+str(n)+'.png', image_out)

# If input image is 8-bit just convert and save one
else:
    # Apply correction LUT
    if Apply_curve:
        curved_image = cv2.LUT(image_padded.astype('uint8'),LUT).astype('uint8')
    else:
        curved_image = image_padded.astype('uint8')
    
    # Invert to negative
    curved_image = cv2.absdiff(curved_image, 255)
    
    if Apply_FFC:
        # Apply flat field correction
        curved_image = FFC(curved_image, image_vig, FFC_strength)
        curved_image = FFC(curved_image, image_vig_2, FFC_strength)

    
    # Squash image for mono LCD
    image_out = Image_squash(curved_image)

    # Save to folder
    cv2.imwrite('Output/Output.png', image_out)