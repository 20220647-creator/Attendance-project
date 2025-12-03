"""
Utility functions for camera and image processing
"""
import cv2
import os
from typing import Optional, Tuple, List
import numpy as np
import time


class CameraUtility:
    """Utility class for camera operations"""

    @staticmethod
    def capture_from_webcam(save_path: str = None, window_name: str = "Capture Face") -> Optional[str]:
        """
        Capture image from webcam

        Args:
            save_path: Path to save the captured image
            window_name: Name of the capture window

        Returns:
            Path to saved image or None if cancelled
        """
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Cannot open webcam")
            return None

        print("\n" + "="*60)
        print("WEBCAM CAPTURE MODE")
        print("="*60)
        print("Press SPACE to capture")
        print("Press ESC to cancel")
        print("="*60)

        captured_image = None

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Cannot read frame")
                break

            # Display instructions on frame
            cv2.putText(frame, "Press SPACE to capture, ESC to cancel",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show frame
            cv2.imshow(window_name, frame)

            key = cv2.waitKey(1) & 0xFF

            # Space key - capture
            if key == ord(' '):
                captured_image = frame.copy()
                print("✓ Image captured!")
                break

            # ESC key - cancel
            elif key == 27:
                print("✗ Capture cancelled")
                break

        cap.release()
        cv2.destroyAllWindows()

        if captured_image is not None and save_path:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, captured_image)
            print(f"✓ Image saved to: {save_path}")
            return save_path

        return None

    @staticmethod
    def capture_multiple_from_webcam(
        save_dir: str,
        student_id: str,
        num_samples: int = 10,
        delay: float = 0.5,
        window_name: str = "Capture Multiple Faces"
    ) -> List[str]:
        """
        Capture multiple face images from webcam for better recognition accuracy

        Args:
            save_dir: Directory to save captured images
            student_id: Student ID for naming files
            num_samples: Number of samples to capture
            delay: Delay between captures (seconds)
            window_name: Name of the capture window

        Returns:
            List of paths to saved images
        """
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Cannot open webcam")
            return []

        print("\n" + "="*60)
        print("MULTIPLE FACE SAMPLES CAPTURE MODE")
        print("="*60)
        print(f"Will capture {num_samples} images for better recognition")
        print("Press SPACE to start capturing")
        print("Press ESC to cancel")
        print("="*60)

        os.makedirs(save_dir, exist_ok=True)
        captured_images = []
        capturing = False
        capture_count = 0
        last_capture_time = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                print("Error: Cannot read frame")
                break

            # Create display frame
            display_frame = frame.copy()

            # Add instructions and progress
            if not capturing:
                cv2.putText(display_frame, "Press SPACE to start, ESC to cancel",
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                progress_text = f"Capturing: {capture_count}/{num_samples}"
                cv2.putText(display_frame, progress_text,
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.putText(display_frame, "Please move your head slightly",
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

            # Draw face detection box
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Use local cascade file to avoid Unicode path issues
            cascade_path = os.path.join('data', 'models', 'haarcascade_frontalface_default.xml')
            if not os.path.exists(cascade_path):
                # Fallback to OpenCV default path
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            cv2.imshow(window_name, display_frame)

            # Handle capturing
            if capturing:
                current_time = time.time()
                if current_time - last_capture_time >= delay:
                    # Save image
                    image_path = os.path.join(save_dir, f"{student_id}_{capture_count}.jpg")
                    cv2.imwrite(image_path, frame)
                    captured_images.append(image_path)
                    capture_count += 1
                    last_capture_time = current_time
                    print(f"✓ Captured image {capture_count}/{num_samples}")

                    # Check if done
                    if capture_count >= num_samples:
                        print(f"✓ All {num_samples} images captured successfully!")
                        break

            key = cv2.waitKey(1) & 0xFF

            # Space key - start capturing
            if key == ord(' ') and not capturing:
                capturing = True
                last_capture_time = time.time()
                print(f"Starting capture of {num_samples} images...")

            # ESC key - cancel
            elif key == 27:
                print("✗ Capture cancelled")
                break

        cap.release()
        cv2.destroyAllWindows()

        if captured_images:
            print(f"✓ {len(captured_images)} images saved to: {save_dir}")

        return captured_images

    @staticmethod
    def detect_faces(image_path: str) -> int:
        """
        Detect number of faces in an image

        Args:
            image_path: Path to the image

        Returns:
            Number of faces detected
        """
        try:
            # Load cascade classifier - use local path to avoid Unicode issues
            cascade_path = os.path.join('data', 'models', 'haarcascade_frontalface_default.xml')
            if not os.path.exists(cascade_path):
                # Fallback to OpenCV default path
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)

            # Read image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            return len(faces)
        except Exception as e:
            print(f"Error detecting faces: {str(e)}")
            return 0

    @staticmethod
    def show_image(image_path: str, window_name: str = "Image", wait_key: bool = True):
        """
        Display an image in a window

        Args:
            image_path: Path to the image
            window_name: Name of the window
            wait_key: Whether to wait for key press
        """
        try:
            image = cv2.imread(image_path)
            if image is not None:
                cv2.imshow(window_name, image)
                if wait_key:
                    print("Press any key to close...")
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()
        except Exception as e:
            print(f"Error displaying image: {str(e)}")

    @staticmethod
    def resize_image(image_path: str, output_path: str, max_width: int = 800, max_height: int = 600) -> bool:
        """
        Resize image to maximum dimensions while maintaining aspect ratio

        Args:
            image_path: Path to input image
            output_path: Path to save resized image
            max_width: Maximum width
            max_height: Maximum height

        Returns:
            True if successful, False otherwise
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False

            height, width = image.shape[:2]

            # Calculate scaling factor
            scale = min(max_width / width, max_height / height)

            if scale < 1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
                cv2.imwrite(output_path, resized)
            else:
                # No resizing needed
                if image_path != output_path:
                    cv2.imwrite(output_path, image)

            return True
        except Exception as e:
            print(f"Error resizing image: {str(e)}")
            return False


class ImageValidator:
    """Validator for image files"""

    VALID_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp'}

    @staticmethod
    def is_valid_image(file_path: str) -> bool:
        """
        Check if file is a valid image

        Args:
            file_path: Path to the file

        Returns:
            True if valid image, False otherwise
        """
        if not os.path.exists(file_path):
            return False

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ImageValidator.VALID_EXTENSIONS:
            return False

        try:
            image = cv2.imread(file_path)
            return image is not None
        except:
            return False

    @staticmethod
    def validate_face_image(image_path: str) -> Tuple[bool, str]:
        """
        Validate if image is suitable for face recognition

        Args:
            image_path: Path to the image

        Returns:
            Tuple of (is_valid, message)
        """
        if not ImageValidator.is_valid_image(image_path):
            return False, "Invalid image file"

        # Check if faces can be detected
        num_faces = CameraUtility.detect_faces(image_path)

        if num_faces == 0:
            return False, "No face detected in image"
        elif num_faces > 1:
            return False, f"Multiple faces detected ({num_faces}). Please use image with single face"

        return True, "Valid face image"

