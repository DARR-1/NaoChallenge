# -*- coding: utf-8 -*-
"""
Camera calibration using chessboard pattern.
Compatible with OpenCV 2.4.5+ (works on NAO).
This script calibrates the camera using a chessboard pattern and saves calibration parameters.
"""

import cv2
import numpy as np
import pickle
import json
import os
import glob

class CameraCalibrator:
    def __init__(self, chessboard_size=(5, 7), square_size=30):
        """
        Initialize the calibrator with a chessboard pattern.
        
        Args:
            chessboard_size: Tuple of (width, height) for the chessboard (inner corners)
            square_size: Size of each square in millimeters
        """
        self.chessboard_size = chessboard_size
        self.square_size = square_size
        
        # Termination criteria for corner refinement
        self.criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Prepare object points (0,0,0), (1,0,0), (2,0,0),...,(width-1, height-1, 0)
        self.objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
        self.objp *= square_size
        
        # Arrays to store object points and image points from all the images
        self.objpoints = []  # 3D point in real world space
        self.imgpoints = []  # 2D points in image plane
        self.image_size = None
        
    def capture_calibration_images(self, camera_index=0, num_images=20):
        """
        Capture images from camera for calibration.
        
        Args:
            camera_index: Index of the camera to use
            num_images: Number of images to capture
        """
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return False
        
        # Set camera properties (use lower resolution for older hardware)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 15)
        
        captured_count = 0
        print("Press SPACE to capture an image, ESC to exit")
        print("Capturing {} images...".format(num_images))
        
        while captured_count < num_images:
            ret, frame = cap.read()
            
            if not ret:
                print("Error: Could not read frame")
                break
            
            self.image_size = frame.shape[:2]
            
            # Display frame
            display_frame = frame.copy()
            cv2.putText(display_frame, "Captured: {}/{}".format(captured_count, num_images), 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(display_frame, "SPACE: Capture | ESC: Exit", 
                       (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow("Calibration - Show Chessboard to camera", display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == 32:  # SPACE
                # Try to detect chessboard corners
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
                
                if ret:
                    # Refine corner positions
                    refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
                    
                    self.objpoints.append(self.objp)
                    self.imgpoints.append(refined_corners)
                    captured_count += 1
                    print("Image {} captured successfully".format(captured_count))
                else:
                    print("Could not detect chessboard. Show more of the board.")
                    
            elif key == 27:  # ESC
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("\nCaptured {} images for calibration".format(captured_count))
        return captured_count > 0
    
    def load_calibration_images(self, images_dir, max_images=None):
        """
        Load calibration images from a directory.
        
        Args:
            images_dir: Directory containing calibration images
            max_images: Maximum number of images to load
        """
        image_files = sorted(glob.glob(os.path.join(images_dir, "*.jpg"))) + \
                     sorted(glob.glob(os.path.join(images_dir, "*.png"))) + \
                     sorted(glob.glob(os.path.join(images_dir, "*.bmp")))
        
        if max_images:
            image_files = image_files[:max_images]
        
        print("Loading {} images from {}".format(len(image_files), images_dir))
        
        for img_path in image_files:
            frame = cv2.imread(img_path)
            if frame is None:
                continue
            
            self.image_size = frame.shape[:2]
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect chessboard corners
            ret, corners = cv2.findChessboardCorners(gray, self.chessboard_size, None)
            
            if ret:
                # Refine corner positions
                refined_corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), self.criteria)
                
                self.objpoints.append(self.objp)
                self.imgpoints.append(refined_corners)
                print("  {}: Detected".format(os.path.basename(img_path)))
            else:
                print("  {}: Not detected".format(os.path.basename(img_path)))
        
        print("Total images with valid detections: {}".format(len(self.objpoints)))
        return len(self.objpoints) > 0
    
    def calibrate(self):
        """
        Perform camera calibration using detected chessboard corners.
        
        Returns:
            Tuple of (camera_matrix, dist_coeffs)
        """
        if len(self.objpoints) == 0:
            print("Error: No calibration images available")
            return None, None
        
        if self.image_size is None:
            print("Error: Image size not set")
            return None, None
        
        print("\nCalibrating with {} images...".format(len(self.objpoints)))
        
        # Calibrate camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            self.objpoints,
            self.imgpoints,
            self.image_size,
            None,
            None
        )
        
        if ret:
            print("Calibration successful!")
            print("\nCamera Matrix:\n{}".format(camera_matrix))
            print("\nDistortion Coefficients:\n{}".format(dist_coeffs))
            
            # Calculate reprojection error
            total_error = 0
            total_points = 0
            for i in range(len(self.objpoints)):
                imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs[i], tvecs[i], 
                                                  camera_matrix, dist_coeffs)
                error = cv2.norm(self.imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
                total_error += error
                total_points += 1
            
            mean_error = total_error / total_points
            print("\nMean reprojection error: {:.4f} pixels".format(mean_error))
            
            return camera_matrix, dist_coeffs
        else:
            print("Calibration failed!")
            return None, None
    
    def save_calibration(self, camera_matrix, dist_coeffs, output_path="calibration.pkl"):
        """
        Save calibration parameters to a file.
        
        Args:
            camera_matrix: Camera matrix from calibration
            dist_coeffs: Distortion coefficients from calibration
            output_path: Path to save calibration file
        """
        if camera_matrix is None or dist_coeffs is None:
            print("Error: Invalid calibration parameters")
            return False
        
        calibration_data = {
            'camera_matrix': camera_matrix.tolist(),
            'dist_coeffs': dist_coeffs.flatten().tolist(),
            'image_size': self.image_size,
            'num_images': len(self.objpoints)
        }
        
        # Save as pickle
        with open(output_path, 'wb') as f:
            pickle.dump(calibration_data, f)
        print("Calibration saved to: {}".format(output_path))
        
        # Also save as JSON for easy reading
        json_path = output_path.replace('.pkl', '.json')
        with open(json_path, 'w') as f:
            json.dump(calibration_data, f, indent=4)
        print("Calibration also saved as JSON: {}".format(json_path))
        
        return True
    
    def update_config_file(self, camera_matrix, dist_coeffs, config_path="config.py"):
        """
        Update the config.py file with calibration parameters.
        
        Args:
            camera_matrix: Camera matrix from calibration
            dist_coeffs: Distortion coefficients from calibration
            config_path: Path to config.py file
        """
        if camera_matrix is None or dist_coeffs is None:
            print("Error: Invalid calibration parameters")
            return False
        
        # Format the matrices
        camera_matrix_str = "CAMERA_MATRIX = [\n"
        for row in camera_matrix:
            camera_matrix_str += "    {},\n".format(row.tolist())
        camera_matrix_str = camera_matrix_str.rstrip(',\n') + "\n]"
        
        dist_coeffs_list = dist_coeffs.flatten().tolist()
        dist_coeffs_str = "DIST_COEFFS = {}".format(dist_coeffs_list)
        
        # Read current config
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Replace or add calibration parameters
            import re
            
            # Replace CAMERA_MATRIX
            if 'CAMERA_MATRIX' in content:
                content = re.sub(
                    r'CAMERA_MATRIX = \[[\s\S]*?\]',
                    camera_matrix_str,
                    content
                )
            else:
                content = camera_matrix_str + "\n\n" + content
            
            # Replace DIST_COEFFS
            if 'DIST_COEFFS' in content:
                content = re.sub(
                    r'DIST_COEFFS = \[.*?\]',
                    dist_coeffs_str,
                    content
                )
            else:
                content = content.rstrip() + "\n" + dist_coeffs_str
            
            with open(config_path, 'w') as f:
                f.write(content)
            
            print("Updated {} with calibration parameters".format(config_path))
            return True
        else:
            print("Error: {} not found".format(config_path))
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Camera calibration using chessboard pattern")
    parser.add_argument("--camera", type=int, default=0, help="Camera index to use")
    parser.add_argument("--num-images", type=int, default=20, help="Number of calibration images")
    parser.add_argument("--images-dir", type=str, help="Directory with pre-captured images")
    parser.add_argument("--output", type=str, default="calibration.pkl", help="Output calibration file")
    parser.add_argument("--update-config", action="store_true", help="Update config.py with calibration")
    parser.add_argument("--config-path", type=str, default="../config.py", help="Path to config.py")
    
    args = parser.parse_args()
    
    # Create calibrator
    calibrator = CameraCalibrator(chessboard_size=(5, 7), square_size=30)
    
    # Capture or load images
    if args.images_dir:
        if not calibrator.load_calibration_images(args.images_dir):
            print("Failed to load calibration images")
            return
    else:
        if not calibrator.capture_calibration_images(args.camera, args.num_images):
            print("Failed to capture calibration images")
            return
    
    # Calibrate
    camera_matrix, dist_coeffs = calibrator.calibrate()
    
    if camera_matrix is not None:
        # Save calibration
        calibrator.save_calibration(camera_matrix, dist_coeffs, args.output)
        
        # Update config if requested
        if args.update_config:
            calibrator.update_config_file(camera_matrix, dist_coeffs, args.config_path)
        
        print("\nCalibration complete!")
    else:
        print("Calibration failed!")


if __name__ == "__main__":
    main()
