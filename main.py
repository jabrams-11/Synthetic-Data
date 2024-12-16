import sys
import random
from pathlib import Path
import bpy

# Add the script directory to sys.path
script_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode"
sys.path.append(script_dir)

from pole_generator import ALSPole, ModifiedVertical, VerticalPole  # Import all pole classes
from renderimages import render_images
from randomize_background import setup_random_background

# Specify the number of poles to generate and render
num_frames = 5  # Set this to the desired number of renders
output_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages"

# List of pole classes to randomly select from
pole_classes = [ALSPole, ModifiedVertical, VerticalPole]

# Loop to generate and render each pole
for image_num in range(num_frames):
    # Randomly select and instantiate a pole class
    PoleClass = random.choice(pole_classes)
    newPole = PoleClass()
    newPole.generate_pole()  # Generate the pole setup
    setup_random_background()

    # Render images and save outputs for the generated pole
    render_images(output_dir, image_num, newPole)  # Render 1 frame per pole generation
