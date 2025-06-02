import json
from collections import defaultdict

def count_coco_annotations(json_path):
    """
    Count annotations per class, images per class, and total images in COCO format dataset.
    
    Args:
        json_path (str): Path to the COCO format JSON file
    
    Returns:
        tuple: (annotations_per_class, images_per_class, total_images, total_annotations)
    """
    
    # Load the COCO JSON file
    with open(json_path, 'r', encoding='utf-8') as f:
        coco_data = json.load(f)
    
    # Get categories for mapping category_id to name
    categories = {cat['id']: cat['name'] for cat in coco_data['categories']}
    
    # Count annotations per category
    annotations_per_class = defaultdict(int)
    
    # Track which images contain each class
    images_per_class = defaultdict(set)
    
    for annotation in coco_data['annotations']:
        category_id = annotation['category_id']
        category_name = categories[category_id]
        image_id = annotation['image_id']
        
        annotations_per_class[category_name] += 1
        images_per_class[category_name].add(image_id)
    
    # Convert sets to counts
    images_per_class_count = {class_name: len(image_set) for class_name, image_set in images_per_class.items()}
    
    # Count total images
    total_images = len(coco_data['images'])
    
    # Count total annotations
    total_annotations = len(coco_data['annotations'])
    
    return dict(annotations_per_class), images_per_class_count, total_images, total_annotations

def print_annotation_stats(json_path):
    """
    Print detailed statistics about the COCO dataset.
    """
    try:
        annotations_per_class, images_per_class, total_images, total_annotations = count_coco_annotations(json_path)
        
        print(f"COCO Dataset Statistics")
        print(f"File: {json_path}")
        print(f"{'='*70}")
        print(f"Total Images: {total_images}")
        print(f"Total Annotations: {total_annotations}")
        print(f"{'='*70}")
        print(f"{'Class':<30} {'Images':<10} {'Annotations':<12} {'Img %':<8} {'Ann %':<8}")
        print(f"{'='*70}")
        
        # Sort classes by annotation count (descending)
        sorted_classes = sorted(annotations_per_class.items(), key=lambda x: x[1], reverse=True)
        
        for class_name, annotation_count in sorted_classes:
            image_count = images_per_class.get(class_name, 0)
            img_percentage = (image_count / total_images) * 100 if total_images > 0 else 0
            ann_percentage = (annotation_count / total_annotations) * 100 if total_annotations > 0 else 0
            
            print(f"{class_name:<30} {image_count:<10} {annotation_count:<12} {img_percentage:>5.1f}% {ann_percentage:>6.1f}%")
        
        print(f"{'='*70}")
        print(f"Average annotations per image: {total_annotations/total_images:.2f}" if total_images > 0 else "No images found")
        
    except FileNotFoundError:
        print(f"Error: File not found at {json_path}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {json_path}")
    except KeyError as e:
        print(f"Error: Missing required key in COCO format: {e}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    # Path to your COCO annotations file
    annotations_path = r"C:\Users\FPL Laptop\Desktop\_annotations.coco.json"
    
    print_annotation_stats(annotations_path)
