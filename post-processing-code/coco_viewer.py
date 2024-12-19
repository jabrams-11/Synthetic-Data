import cv2
import json
import numpy as np
import os

# Paths to directories and JSON annotation file
images_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages"  # Replace with the path to your images directory
json_path = r'RenderedImages\coco_annotations.json'
output_dir = r'RenderedImages\labeled_images'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load the JSON annotations
with open(json_path) as f:
    coco_data = json.load(f)

# Extract annotations, images, and category data from the JSON
annotations = coco_data['annotations']
images_data = {img['id']: img['file_name'] for img in coco_data['images']}
categories = {cat['id']: cat['name'] for cat in coco_data['categories']}

# Function to generate a random color for each instance mask
def random_color():
    return np.random.randint(0, 255, size=3).tolist()

# Loop through each image in the directory
for image_info in coco_data['images']:
    image_filename = image_info['file_name']
    image_path = os.path.join(images_dir, image_filename)

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Image {image_filename} not found. Skipping.")
        continue

    # Get the annotations for this specific image
    height, width, _ = image.shape
    image_id = image_info['id']
    image_annotations = [ann for ann in annotations if ann['image_id'] == image_id]

    # Loop over each annotation for this image
    for ann in image_annotations:
        segmentation = ann['segmentation']
        category_id = ann['category_id']
        bbox = ann['bbox']
        label = categories[category_id]

        # Random color for each mask
        mask_color = random_color()

        # Draw the bounding box
        x, y, w, h = bbox
        top_left = (int(x), int(y))
        bottom_right = (int(x + w), int(y + h))
        cv2.rectangle(image, top_left, bottom_right, mask_color, 2)

        # Put the label above the bounding box
        label_position = (int(x), int(y) - 10)
        cv2.putText(image, label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, mask_color, 3)

        # Create a blank mask with the same dimensions as the image
        mask = np.zeros((height, width), dtype=np.uint8)

        # If segmentation is in polygons (list of points)
        if isinstance(segmentation, list):
            # Each segmentation can have multiple polygons
            for polygon in segmentation:
                points = np.array(polygon).reshape(-1, 2).astype(np.int32)
                cv2.fillPoly(mask, [points], 255)

        # Apply color to mask and overlay on the image
        color_mask = np.zeros_like(image)
        color_mask[mask == 255] = mask_color

        # Blend the mask with the original image
        image = cv2.addWeighted(image, 1.0, color_mask, 0.5, 0)

    # Save the labeled image in the output directory
    output_path = os.path.join(output_dir, image_filename)
    cv2.imwrite(output_path, image)
    print(f"Saved labeled image to {output_path}")
