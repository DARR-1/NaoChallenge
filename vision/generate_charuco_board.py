"""
Generate a ChArUco board for camera calibration.
This script creates a ChArUco board image that can be printed for calibration purposes.
"""

# -*- coding: utf-8 -*-
import cv2
import os

def generate_charuco_board(squares_x=5, squares_y=7, square_length=40, marker_length=30, 
                          output_path="charuco_board.png", dpi=300):
    """
    Generate a ChArUco board image.
    
    Args:
        squares_x: Number of squares in X direction
        squares_y: Number of squares in Y direction
        square_length: Size of each square in pixels
        marker_length: Size of each ArUco marker in pixels
        output_path: Path where to save the generated board
        dpi: DPI for printing (affects final size)
    """
    # Define the dictionary to use
    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_250)
    
    # Create the board for OpenCV 3.x compatibility
    board = cv2.aruco.CharucoBoard_create(squares_x, squares_y, square_length, 
                                          int(marker_length), aruco_dict)
    
    # Generate the image
    img = board.draw((squares_x * square_length, squares_y * square_length))
    
    # Save the image
    cv2.imwrite(output_path, img)
    print("ChArUco board generated and saved to: {}".format(output_path))
    print("Board size: {}x{} squares".format(squares_x, squares_y))
    print("Square length: {} pixels".format(square_length))
    print("Marker length: {} pixels".format(marker_length))
    
    # Display info for printing
    height_mm = squares_y * square_length * 25.4 / dpi
    width_mm = squares_x * square_length * 25.4 / dpi
    print("\nFor printing at {} DPI:".format(dpi))
    print("  Recommended size: {:.1f}mm x {:.1f}mm".format(width_mm, height_mm))
    print("  Or: {:.1f}in x {:.1f}in".format(width_mm/25.4, height_mm/25.4))
    
    return img

if __name__ == "__main__":
    # Create output directory if it doesn't exist
    output_dir = "calibration_boards"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, "charuco_board.png")
    generate_charuco_board(
        squares_x=5,
        squares_y=7,
        square_length=500,      # 21.2cm ancho x 29.6cm alto (A4)
        marker_length=375,
        output_path=output_file,
        dpi=300
    )
