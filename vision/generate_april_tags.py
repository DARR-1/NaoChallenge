# -*- coding: utf-8 -*-
"""
Generate individual AprilTag images for printing or testing.
Uses OpenCV ArUco module (no external compilation needed).
"""

import cv2
import numpy as np
import os


# Map family names to OpenCV constants
FAMILY_MAP = {
    "tag36h11": cv2.aruco.DICT_APRILTAG_36h11,
    "tag25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "tag16h5": cv2.aruco.DICT_APRILTAG_16h5,
}


def generate_april_tag(tag_id, tag_size_px=400, family="tag36h11", output_path=None, add_border=True):
    """
    Generate a single AprilTag image using OpenCV.
    
    Args:
        tag_id: ID of the tag
        tag_size_px: Size of the tag in pixels
        family: AprilTag family (tag36h11, tag25h9, tag16h5)
        output_path: Path to save the image (if None, returns numpy array)
        add_border: Whether to add white border around the tag (default: True)
    
    Returns:
        numpy array of the tag image if output_path is None
    """
    try:
        # Get the dictionary
        if family not in FAMILY_MAP:
            print("Error: Family '{}' not supported. Use: {}".format(family, list(FAMILY_MAP.keys())))
            return None
        
        aruco_dict = cv2.aruco.Dictionary_get(FAMILY_MAP[family])
        
        # Generate the tag image using drawMarker for OpenCV 3.x compatibility
        tag_img = cv2.aruco.drawMarker(aruco_dict, tag_id, tag_size_px)
        
    except Exception as e:
        print("Error generating tag {}: {}".format(tag_id, e))
        return None
    
    if tag_img is None:
        print("Error: Could not generate tag {} from family {}".format(tag_id, family))
        return None
    
    # Convert to uint8 if needed and scale to desired size
    if len(tag_img.shape) == 3:
        tag_img = cv2.cvtColor(tag_img, cv2.COLOR_BGR2GRAY)
    
    tag_img_resized = cv2.resize(tag_img, (tag_size_px, tag_size_px), interpolation=cv2.INTER_NEAREST)
    
    # Add white border if requested (10% of size)
    if add_border:
        border = int(tag_size_px * 0.1)
        tag_img_final = cv2.copyMakeBorder(
            tag_img_resized,
            border, border, border, border,
            cv2.BORDER_CONSTANT,
            value=255
        )
        border_text = " with border"
    else:
        tag_img_final = tag_img_resized
        border_text = " (no border)"
    
    if output_path:
        cv2.imwrite(output_path, tag_img_final)
        print("AprilTag {} ({}){} saved to: {}".format(tag_id, family, border_text, output_path))
    
    return tag_img_final


def generate_april_tags_grid(tag_ids, tag_size_px=200, family="tag36h11", 
                             cols=3, output_path="april_tags_grid.png", add_border=True):
    """
    Generate a grid of AprilTags for printing.
    
    Args:
        tag_ids: List of tag IDs to generate
        tag_size_px: Size of each tag in pixels
        family: AprilTag family (tag36h11, tag25h9, tag16h5)
        cols: Number of columns in the grid
        output_path: Path to save the grid image
        add_border: Whether to add white border around each tag (default: True)
    """
    if family not in FAMILY_MAP:
        print("Error: Family '{}' not supported. Use: {}".format(family, list(FAMILY_MAP.keys())))
        return None
    
    if not tag_ids:
        print("Error: No tag IDs provided")
        return None
    
    aruco_dict = cv2.aruco.Dictionary_get(FAMILY_MAP[family])
    tags = []
    
    # Generate all tags
    for tag_id in tag_ids:
        try:
            tag_img = cv2.aruco.drawMarker(aruco_dict, tag_id, tag_size_px)
            
            if tag_img is not None:
                # Convert to grayscale if needed
                if len(tag_img.shape) == 3:
                    tag_img = cv2.cvtColor(tag_img, cv2.COLOR_BGR2GRAY)
                
                # Resize
                tag_resized = cv2.resize(tag_img, (tag_size_px, tag_size_px), interpolation=cv2.INTER_NEAREST)
                
                # Add border if requested
                if add_border:
                    border = int(tag_size_px * 0.1)
                    tag_bordered = cv2.copyMakeBorder(
                        tag_resized,
                        border, border, border, border,
                        cv2.BORDER_CONSTANT,
                        value=255
                    )
                else:
                    tag_bordered = tag_resized
                
                # Add text with ID
                text_img = np.ones((50, tag_bordered.shape[1]), dtype=np.uint8) * 255
                cv2.putText(text_img, "ID: {}".format(tag_id), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
                tag_with_text = np.vstack([tag_bordered, text_img])
                tags.append(tag_with_text)
                print("  Tag {}: Generated".format(tag_id))
            else:
                print("  Tag {}: Failed to generate".format(tag_id))
        except Exception as e:
            print("  Tag {}: Error - {}".format(tag_id, e))
    
    if not tags:
        print("Error: No valid tags generated")
        return None
    
    # Create grid
    rows = (len(tags) + cols - 1) // cols  # Ceiling division
    
    # Pad with blank images if needed
    tag_height = tags[0].shape[0]
    tag_width = tags[0].shape[1]
    blank_tag = np.ones((tag_height, tag_width), dtype=np.uint8) * 255
    
    while len(tags) < rows * cols:
        tags.append(blank_tag)
    
    # Create rows
    grid_rows = []
    for r in range(rows):
        row_tags = tags[r*cols:(r+1)*cols]
        row_img = np.hstack(row_tags)
        grid_rows.append(row_img)
    
    # Stack rows
    grid = np.vstack(grid_rows)
    
    # Save
    cv2.imwrite(output_path, grid)
    border_status = "with borders" if add_border else "without borders"
    print("\nAprilTag grid saved to: {}".format(output_path))
    print("  Grid size: {}x{} ({} tags)".format(rows, cols, len(tag_ids)))
    print("  Tag family: {}".format(family))
    print("  Tag size: {}px ({:.1f}mm at 300 DPI) {}".format(tag_size_px, tag_size_px/300*25.4, border_status))
    
    return grid


def get_tag_family_info(family="tag36h11"):
    """Get info about a tag family."""
    family_info = {
        "tag36h11": {"max_id": 586, "bits": 36, "min_distance": 11, "supported": True},
        "tag25h9": {"max_id": 242, "bits": 25, "min_distance": 9, "supported": True},
        "tag16h5": {"max_id": 29, "bits": 16, "min_distance": 5, "supported": True},
        "tagCircle21h7": {"max_id": 620, "bits": 21, "min_distance": 7, "supported": False},
        "tagCircle49h12": {"max_id": 4200, "bits": 49, "min_distance": 12, "supported": False},
        "tagStandard41h6": {"max_id": 2320, "bits": 41, "min_distance": 6, "supported": False},
        "tagStandard52h13": {"max_id": 47999, "bits": 52, "min_distance": 13, "supported": False},
    }
    
    if family in family_info:
        return family_info[family]
    else:
        return {"error": "Unknown family: {}".format(family)}


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate AprilTag images using OpenCV")
    parser.add_argument("--id", type=int, help="Single tag ID to generate")
    parser.add_argument("--ids", type=int, nargs="+", help="Multiple tag IDs (e.g., --ids 0 1 2 3)")
    parser.add_argument("--size", type=int, default=200, help="Tag size in pixels (default: 200)")
    parser.add_argument("--family", type=str, default="tag36h11", 
                       help="Tag family (tag36h11, tag25h9, tag16h5)")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--grid", action="store_true", help="Generate grid of tags")
    parser.add_argument("--cols", type=int, default=3, help="Number of columns in grid (default: 3)")
    parser.add_argument("--no-border", action="store_true", help="Generate tags without white border")
    parser.add_argument("--info", action="store_true", help="Show family info")
    
    args = parser.parse_args()
    
    # Show family info
    if args.info:
        print("\nAprilTag Family Information:")
        print("-" * 60)
        print("{:<20} | {:<8} | {:<6} | {:<10} | {:<10}".format('Family', 'Max ID', 'Bits', 'Distance', 'Status'))
        print("-" * 60)
        families = ["tag36h11", "tag25h9", "tag16h5", "tagCircle21h7", 
                   "tagCircle49h12", "tagStandard41h6", "tagStandard52h13"]
        for fam in families:
            info = get_tag_family_info(fam)
            if "error" not in info:
                status = "Supported" if info.get("supported", False) else "Not supported"
                print("{:<20} | {:<8} | {:<6} | {:<10} | {:<10}".format(fam, str(info['max_id']), str(info['bits']), str(info['min_distance']), status))
        print("\n(Only tag36h11, tag25h9, tag16h5 are supported by OpenCV ArUco)")
        return
    
    # Create output directory
    output_dir = "april_tags"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    add_border = not args.no_border
    
    # Generate grid
    if args.grid and (args.id or args.ids):
        tag_ids = args.ids if args.ids else [args.id]
        output_file = args.output or os.path.join(output_dir, "tags_grid_{}.png".format(args.family))
        print("\nGenerating AprilTag grid...")
        generate_april_tags_grid(tag_ids, args.size, args.family, args.cols, output_file, add_border)
    
    # Generate single tag
    elif args.id is not None:
        output_file = args.output or os.path.join(output_dir, "tag_{}_{}.png".format(args.id, args.family))
        print("\nGenerating AprilTag {}...".format(args.id))
        generate_april_tag(args.id, args.size, args.family, output_file, add_border)
    
    # Generate multiple tags
    elif args.ids:
        print("\nGenerating {} AprilTags...".format(len(args.ids)))
        for tag_id in args.ids:
            output_file = os.path.join(output_dir, "tag_{}_{}.png".format(tag_id, args.family))
            generate_april_tag(tag_id, args.size, args.family, output_file, add_border)
        print("\nGenerated {} tags in {}/ ".format(len(args.ids), output_dir))
    
    else:
        # Default: generate first 4 tags as example
        print("Generating example tags (0-3) in a grid...")
        output_file = os.path.join(output_dir, "tags_example_{}.png".format(args.family))
        generate_april_tags_grid([0, 1, 2, 3], args.size, args.family, 2, output_file, add_border)


if __name__ == "__main__":
    main()
