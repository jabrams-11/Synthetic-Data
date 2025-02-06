import cv2
import numpy as np
import json
import os

# Load the label mappings from the JSON file (handles multiple JSON objects on separate lines)
label_mappings = {}
with open(r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages\all_frame_mappings.json", "r") as mapping_file:
	for line in mapping_file:
		line_data = json.loads(line)
		label_mappings.update(line_data)

# Prepare the COCO-format structure
coco_annotations = {
	"images": [],
	"annotations": [],
	"categories": []
}

# Set of unique categories
category_id_map = {}
category_id_counter = 1

# Paths to images and masks directories
images_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages"  # Replace with actual path to images directory
masks_dir = r"C:\Users\FPL Laptop\Desktop\BlenderSyntheticDataCode\RenderedImages"    # Replace with actual path to masks directory

# Initialize image and annotation ID counters
image_id = 1
annotation_id = 1

# Loop through each image-mask pair in the directory
for image_filename in sorted(os.listdir(images_dir)):
	if not image_filename.startswith("Image_") or not image_filename.endswith(".png"):
		continue
	print(image_filename)
	# Load the mask for the corresponding image
	mask_filename = image_filename.replace("Image_", "Mask_")
	mask_path = os.path.join(masks_dir, mask_filename)
	mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
	image_base_name = os.path.splitext(image_filename)[0]
	# Skip if no mapping exists for the current image
	if image_base_name not in label_mappings:
		print("continue")
		continue

	# Prepare image information
	image_info = {
		"id": image_id,
		"width": mask.shape[1],
		"height": mask.shape[0],
		"file_name": image_filename
	}
	coco_annotations["images"].append(image_info)

	# Get object labels for the current image
	object_labels = label_mappings[image_base_name]

	# Loop through each unique pass index in the mask
	unique_ids = np.unique(mask)
	for obj_id in unique_ids:
		if obj_id == 0 or str(obj_id) not in object_labels:  # Skip background or unmapped objects
			continue
		
		# Get the label name for the current object ID
		label_name = object_labels[str(obj_id)]

		# Assign a category ID if the label is new
		if label_name not in category_id_map:
			category_id_map[label_name] = category_id_counter
			coco_annotations["categories"].append({
				"id": category_id_counter,
				"name": label_name,
				"supercategory": "none"
			})
			category_id_counter += 1

		# Create a binary mask for the current object
		binary_mask = np.where(mask == obj_id, 255, 0).astype(np.uint8)

		# Find contours for the object
		contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		segmentation = [contour.flatten().tolist() for contour in contours if len(contour) >= 3]

		# Calculate bounding box and area
		x, y, w, h = cv2.boundingRect(binary_mask)
		area = np.sum(binary_mask) / 255

		# Add annotation for this object
		annotation = {
			"id": annotation_id,
			"image_id": image_id,
			"category_id": category_id_map[label_name],
			"segmentation": segmentation,
			"area": area,
			"bbox": [x, y, w, h],
			"iscrowd": 0
		}
		coco_annotations["annotations"].append(annotation)
		annotation_id += 1

	image_id += 1

# Save the COCO format JSON in the RenderedImages directory
output_path = os.path.join(images_dir, "coco_annotations.json")
with open(output_path, "w") as outfile:
    json.dump(coco_annotations, outfile)

print("COCO annotations saved to RenderedImages folder.")