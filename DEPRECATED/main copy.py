import sys
import random
from pathlib import Path
import bpy
import time
# Add the script directory to sys.path
script_dir = r"C:\Users\jackp\Desktop\FPL-SyntheticDataProject\Synthetic-Data"
sys.path.append(script_dir)

from pole_generator import *  # Import all pole classes
from renderimages import render_images
from randomize_background import setup_random_background

# Specify the number of poles to generate and render
num_frames = 1  # Set this to the desired number of renders
output_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages"

# List of pole classes to randomly select from
pole_classes = [ALSPole, ALSPole2, ModifiedVertical, VerticalPole, DeadendPole, CrossarmPole, ALS_Fuse_Crossarm, ALS_Fuse_Crossarm_2]


PoleClass = random.choice(pole_classes)
newPole = ModifiedVertical()
newPole.generate_pole()  # Generate the pole setup
print('POLE GENERATED----------------------------')
#setup_random_background()

#setup_random_background()
'''
# Loop to generate and render each pole
for image_num in range(num_frames):
    # Randomly select and instantiate a pole class
    PoleClass = random.choice(pole_classes)
    newPole = ModifiedVertical(pole_type = 'WoodPole', aetx=True, ats=True, surge_arresters=True,anomaly=True, phases=2)
    newPole.generate_pole()  # Generate the pole setup
    #setup_random_background()

    # Render images and save outputs for the generated pole
    render_images(output_dir, image_num, newPole)  # Render 1 frame per pole generation
'''