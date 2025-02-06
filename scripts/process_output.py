import os
import cv2
import json
import numpy as np
import yaml
from pathlib import Path

def load_config(config_path="configs/rendering.yaml"):
	"""Load rendering configuration from YAML file."""
	config_path = Path(config_path)
	if not config_path.is_absolute():
		# Get the project root directory (parent of scripts directory)
		project_root = Path(__file__).parent.parent
		config_path = project_root / config_path
	
	with open(config_path, 'r') as f:
		return yaml.safe_load(f)

def generate_coco_annotations(output_dir=None):
	"""
	Convert Blender synthetic data output to COCO format.
	
	Args:
		output_dir: Optional path to override the output directory from config
	"""
	if output_dir is None:
		config = load_config()
		output_dir = Path(config['output']['base_path'])
	else:
		output_dir = Path(output_dir)
	
	mapping_file_path = output_dir / "all_frame_mappings.json"
	
	if not mapping_file_path.exists():
		raise FileNotFoundError(f"Mapping file not found at {mapping_file_path}")
	
	print(f"Loading mappings from: {mapping_file_path}")
	with open(mapping_file_path, "r") as mapping_file:
		label_mappings = json.load(mapping_file)
	print(f"Found {len(label_mappings)} image mappings")

	# Prepare the COCO-format structure
	coco_annotations = {
		"images": [],
		"annotations": [],
		"categories": []
	}

	# Set of unique categories
	category_id_map = {}
	category_id_counter = 1

	# Initialize image and annotation ID counters
	image_id = 1
	annotation_id = 1

	# Loop through each mapping entry first
	for mapping_name in sorted(label_mappings.keys()):
		# Convert render_XXXX to Image_XXXX
		image_number = mapping_name.split('_')[1]  # Get the number part (e.g., "0000")
		
		# Construct the actual filenames
		image_filename = f"Image_{image_number}.png"
		mask_filename = f"Mask_{image_number}.png"
		
		image_path = output_dir / image_filename
		mask_path = output_dir / mask_filename
		
		if not image_path.exists():
			print(f"Warning: Image file not found: {image_path}")
			continue
			
		if not mask_path.exists():
			print(f"Warning: Mask file not found: {mask_path}")
			continue
			
		print(f"Processing image: {image_filename}")
		mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
		if mask is None:
			print(f"Warning: Failed to read mask: {mask_path}")
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
		object_labels = label_mappings[mapping_name]
		print(f"Found {len(object_labels)} objects in {mapping_name}")

		# Loop through each unique pass index in the mask
		unique_ids = np.unique(mask)
		print(f"Unique IDs in mask: {unique_ids}")
		
		for obj_id in unique_ids:
			if obj_id == 0:  # Skip background
				continue
				
			str_obj_id = str(obj_id)
			if str_obj_id not in object_labels:
				print(f"Warning: Object ID {obj_id} not found in mappings")
				continue
			
			# Get the label name for the current object ID
			label_name = object_labels[str_obj_id]

			# Assign a category ID if the label is new
			if label_name not in category_id_map:
				category_id_map[label_name] = category_id_counter
				coco_annotations["categories"].append({
					"id": category_id_counter,
					"name": label_name,
					"supercategory": "utility_pole"
				})
				category_id_counter += 1

			# Create a binary mask for the current object
			binary_mask = np.where(mask == obj_id, 255, 0).astype(np.uint8)

			# Find contours for the object
			contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			segmentation = [contour.flatten().tolist() for contour in contours if len(contour) >= 3]

			if not segmentation:
				print(f"Warning: No valid contours found for object {obj_id} ({label_name})")
				continue

			# Calculate bounding box and area
			x, y, w, h = cv2.boundingRect(binary_mask)
			area = float(np.sum(binary_mask) / 255)  # Convert to float for JSON serialization

			# Add annotation for this object
			annotation = {
				"id": annotation_id,
				"image_id": image_id,
				"category_id": category_id_map[label_name],
				"segmentation": segmentation,
				"area": area,
				"bbox": [float(x), float(y), float(w), float(h)],
				"iscrowd": 0
			}
			coco_annotations["annotations"].append(annotation)
			annotation_id += 1

		image_id += 1

	# Save the COCO format JSON
	output_path = output_dir / "coco_annotations.json"
	with open(output_path, "w") as outfile:
		json.dump(coco_annotations, outfile, indent=2)

	print(f"COCO annotations saved to {output_path}")
	return output_path

def visualize_annotations(coco_data, images_dir, output_dir):
    """
    Draw COCO annotations on images and save them to a visualization directory.
    
    Args:
        coco_data: COCO format annotations dictionary
        images_dir: Directory containing the original images
        output_dir: Directory to save visualizations
    """
    # Create visualization directory
    vis_dir = Path(output_dir) / "visualizations"
    vis_dir.mkdir(exist_ok=True)
    
    # Create color map for categories
    categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
    color_map = {}
    for cat_id in categories:
        color_map[cat_id] = tuple(np.random.randint(0, 255, 3).tolist())
    
    # Group annotations by image_id
    image_annotations = {}
    for ann in coco_data['annotations']:
        image_id = ann['image_id']
        if image_id not in image_annotations:
            image_annotations[image_id] = []
        image_annotations[image_id].append(ann)
    
    # Process each image
    for img_info in coco_data['images']:
        image_path = Path(images_dir) / img_info['file_name']
        if not image_path.exists():
            print(f"Warning: Image not found: {image_path}")
            continue
            
        # Read image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Warning: Could not read image: {image_path}")
            continue
            
        # Draw annotations
        for ann in image_annotations.get(img_info['id'], []):
            color = color_map[ann['category_id']]
            
            # Draw segmentation
            for segment in ann['segmentation']:
                pts = np.array(segment).reshape((-1, 2)).astype(np.int32)
                cv2.polylines(image, [pts], True, color, 2)
            
            # Draw bounding box
            x, y, w, h = map(int, ann['bbox'])
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            
            # Add label
            category_name = categories[ann['category_id']]
            cv2.putText(image, category_name, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Save visualization
        output_path = vis_dir / f"viz_{img_info['file_name']}"
        cv2.imwrite(str(output_path), image)
        print(f"Saved visualization: {output_path}")

def process_outputs(output_dir=None, save_coco=True, visualize=True):
    """
    Process the synthetic data outputs to generate COCO annotations and visualizations.
    
    Args:
        output_dir: Optional path to override the output directory from config
        save_coco: Whether to save COCO format annotations
        visualize: Whether to create visualization images with annotations
    """
    if output_dir is None:
        config = load_config()
        output_dir = Path(config['output']['base_path'])
    else:
        output_dir = Path(output_dir)
    
    coco_path = None
    if save_coco:
        coco_path = generate_coco_annotations(output_dir)
        print(f"Saved COCO annotations to: {coco_path}")
    
    if visualize:
        if coco_path is None:
            coco_path = output_dir / "coco_annotations.json"
        
        if not coco_path.exists():
            print("Error: COCO annotations not found. Cannot create visualizations.")
            return
        
        with open(coco_path, 'r') as f:
            coco_data = json.load(f)
        
        visualize_annotations(coco_data, output_dir, output_dir)
        print(f"Saved visualizations to: {output_dir}/visualizations")

if __name__ == "__main__":
	try:
		process_outputs()
		print("Successfully processed dataset")
	except Exception as e:
		print(f"Error processing dataset: {str(e)}")
		exit(1)
	exit(0)