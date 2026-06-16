# -*- coding: utf-8 -*-
"""
Simple calibration workflow using ChArUco board.
Run this script to perform complete camera calibration in steps.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calibrate_april_tags import CharucoCalibrator
from generate_charuco_board import generate_charuco_board


def print_header(text):
    print("\n" + "="*60)
    print("  {}".format(text))
    print("="*60)


def step_1_generate_board():
    """Step 1: Generate ChArUco board"""
    print_header("STEP 1: Generate ChArUco Board")
    
    output_dir = "calibration_boards"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, "charuco_board.png")
    
    if os.path.exists(output_file):
        response = raw_input("Board already exists. Regenerate? (y/n): ").lower()
        if response != 'y':
            print("Using existing board: {}".format(output_file))
            return output_file
    
    print("\nGenerating ChArUco board...")
    generate_charuco_board(
        squares_x=5,
        squares_y=7,
        square_length=40,
        marker_length=30,
        output_path=output_file,
        dpi=300
    )
    
    print("\n- Board generated: {}".format(output_file))
    print("NEXT STEPS:")
    print("  1. Print the board on A4 or letter paper at 100% scale (no scaling)")
    print("  2. Mount it on a rigid surface (cardboard or foam board)")
    print("  3. Ensure good lighting when capturing")
    
    return output_file


def step_2_capture_images():
    """Step 2: Capture calibration images"""
    print_header("STEP 2: Capture Calibration Images")
    
    camera_choice = raw_input("\nCapture images now? (y/n): ").lower()
    if camera_choice != 'y':
        images_dir = raw_input("Enter path to directory with pre-captured images (or press Enter to skip): ").strip()
        return images_dir if images_dir else None
    
    num_images = raw_input("Number of images to capture (default 20): ").strip()
    num_images = int(num_images) if num_images else 20
    
    camera_index = raw_input("Camera index (default 0): ").strip()
    camera_index = int(camera_index) if camera_index else 0
    
    print("\nStarting camera capture (camera {})...".format(camera_index))
    print("   Instructions:")
    print("   - Show the ChArUco board to the camera from different angles")
    print("   - Press SPACE to capture each image")
    print("   - Press ESC when done or when you have enough images")
    
    calibrator = CharucoCalibrator()
    calibrator.capture_calibration_images(camera_index=camera_index, num_images=num_images)
    
    return None


def step_3_calibrate(images_dir=None):
    """Step 3: Perform calibration"""
    print_header("STEP 3: Perform Calibration")
    
    calibrator = CharucoCalibrator()
    
    if images_dir:
        print("Loading images from {}...".format(images_dir))
        if not calibrator.load_calibration_images(images_dir):
            print("Failed to load images")
            return None, None, None
    else:
        print("Using captured images...")
        # Images should have been captured in step 2
    
    print("\nStarting calibration...")
    camera_matrix, dist_coeffs = calibrator.calibrate()
    
    if camera_matrix is not None:
        print("\nCalibration successful!")
        print("\nCalibration Parameters:")
        print("-" * 40)
        print("CAMERA_MATRIX = [")
        for row in camera_matrix:
            print("    {},".format(row.tolist()))
        print("]")
        print("\nDIST_COEFFS = {}".format(dist_coeffs.flatten().tolist()))
        
        return calibrator, camera_matrix, dist_coeffs
    else:
        print("\nCalibration failed!")
        return None, None, None


def step_4_save_calibration(calibrator, camera_matrix, dist_coeffs):
    """Step 4: Save calibration results"""
    print_header("STEP 4: Save Calibration Results")
    
    if camera_matrix is None:
        print("No calibration data to save")
        return
    
    # Save to pickle file
    output_file = raw_input("Output file for calibration (default: calibration.pkl): ").strip()
    output_file = output_file if output_file else "calibration.pkl"
    
    calibrator.save_calibration(camera_matrix, dist_coeffs, output_file)
    
    # Update config file
    update_config = raw_input("\nUpdate config.py with calibration parameters? (y/n): ").lower()
    if update_config == 'y':
        config_path = raw_input("Path to config.py (default: ../config.py): ").strip()
        config_path = config_path if config_path else "../config.py"
        
        if os.path.exists(config_path):
            calibrator.update_config_file(camera_matrix, dist_coeffs, config_path)
            print("Updated {}".format(config_path))
        else:
            print("File not found: {}".format(config_path))
    
    print("\nCalibration saved!")


def main():
    """Main calibration workflow"""
    print("\n" + "="*60)
    print("  Camera Calibration Tool - ChArUco Board")
    print("="*60)
    
    # Step 1: Generate board
    step_1_generate_board()
    
    raw_input("\n\nPress Enter to continue to image capture...")
    
    # Step 2: Capture images
    images_dir = step_2_capture_images()
    
    raw_input("\n\nPress Enter to start calibration...")
    
    # Step 3: Calibrate
    calibrator, camera_matrix, dist_coeffs = step_3_calibrate(images_dir)
    
    if camera_matrix is not None:
        raw_input("\n\nPress Enter to save results...")
        
        # Step 4: Save results
        step_4_save_calibration(calibrator, camera_matrix, dist_coeffs)
        
        print_header("CALIBRATION COMPLETE")
        print("Your camera is now calibrated!")
        print("\nYou can now use the calibration parameters for:")
        print("  - Precise April tag detection")
        print("  - Object detection and tracking")
        print("  - Robot vision tasks")
    else:
        print("\nCalibration process failed")


if __name__ == "__main__":
    main()
