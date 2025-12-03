"""
Initialize Haar Cascade classifier to avoid Unicode path issues
This script copies the Haar Cascade XML file to a local directory
"""
import cv2
import shutil
import os


def initialize_haar_cascade():
    """Copy Haar Cascade to local directory to avoid Unicode path issues"""
    try:
        # Create models directory
        models_dir = os.path.join('data', 'models')
        os.makedirs(models_dir, exist_ok=True)

        # Path to destination
        cascade_dest = os.path.join(models_dir, 'haarcascade_frontalface_default.xml')

        # Check if already exists
        if os.path.exists(cascade_dest):
            print(f"✓ Haar Cascade already exists at: {cascade_dest}")
            return True

        # Copy from OpenCV installation
        cascade_src = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')

        if not os.path.exists(cascade_src):
            print(f"✗ Error: Haar Cascade not found at: {cascade_src}")
            return False

        shutil.copy(cascade_src, cascade_dest)
        print(f"✓ Haar Cascade copied to: {cascade_dest}")
        return True

    except Exception as e:
        print(f"✗ Error initializing Haar Cascade: {str(e)}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("Initializing Haar Cascade Classifier")
    print("="*60)
    initialize_haar_cascade()
    print("="*60)

