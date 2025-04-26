"""
Simple script to display an image full-screen on a Raspberry Pi 4 for a set time

There is a button wired up to the pi which starts the exposure when pressed.
The UV exposure light is also controlled by the pi.

@author: Andrew
"""

# You need the OpenCV and gpiozero python libraries installed on the pi
import cv2
import gpiozero as IO

image_path = "../Pictures/Exposure_test/05.png" # Location of the image to be printed
image = cv2.imread(image_path)
exp_time = 240000 # Exposure time in milliseconds

Button_LED = IO.LED(4) # I/O pin for the button light
UV_Light = IO.LED(12) # I/O pin for the UV exposure light
Button = IO.Button(23) # I/O for the button itself

# This function is what actually displays the image
def Print_image(image,exp_time):
    cv2.namedWindow("print", cv2.WINDOW_NORMAL) # Create an image window
    cv2.setWindowProperty("print", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN) # Make the window fullscreen
    Button_LED.off() # Turn off the button LED now that exposure is starting
    cv2.imshow("print", image) # Show the image to be printed
    cv2.waitKey(2000) # Wait 2 seconds to allow the image to display, pi can be slow with big image files
    UV_Light.on() # Turn on the UV light source
    cv2.waitKey(exp_time) # Wait for the exposure duration
    UV_Light.off() # Turn off the UV light source
    cv2.destroyWindow("print") # Clear the fullscreen image
    return

Button_LED.on() # Turn on the button light when the printer is ready to go
Button.wait_for_active() # Wait for the button to be pushed
Print_image(image,exp_time) # Call the image show function when the button is pushed

print("Done") # Fin