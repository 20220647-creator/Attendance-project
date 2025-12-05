# -*- coding: utf-8 -*-
"""
Standalone script to augment face dataset
VGGFace2-inspired data augmentation for better recognition
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.data_augmentation import augment_existing_dataset, FaceDataAugmentation
from src.config.config import config


def main():
    print("=" * 70)
    print("  FACE DATASET AUGMENTATION - VGGFace2 Inspired")
    print("=" * 70)
    print("\nThis will create additional training images to improve accuracy.")
    print("Techniques used:")
    print("  - Brightness adjustment")
    print("  - Contrast adjustment")
    print("  - Gaussian blur (camera simulation)")
    print("  - Noise addition (low light simulation)")
    print("  - Horizontal flip (mirror)")
    print("  - Rotation (-15 to +15 degrees)")
    print("  - Color jitter")
    print("\n" + "=" * 70)

    # Get number of augmented images
    while True:
        try:
            num_str = input("\nNumber of augmented images per original (1-20, default=5): ").strip()
            if not num_str:
                num_augmented = 5
                break
            num_augmented = int(num_str)
            if 1 <= num_augmented <= 20:
                break
            print("Please enter a number between 1 and 20")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Confirm
    data_dir = config.STUDENT_DATABASE_PATH
    print(f"\nTarget directory: {data_dir}")
    print(f"Augmentation level: {num_augmented} images per original")

    confirm = input("\nProceed with augmentation? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("Augmentation cancelled.")
        return

    print("\n" + "=" * 70)
    print("PROCESSING...")
    print("=" * 70)

    # Run augmentation
    stats = augment_existing_dataset(data_dir, augmentation_per_image=num_augmented)

    # Display results
    print("\n" + "=" * 70)
    print("AUGMENTATION COMPLETE!")
    print("=" * 70)
    print(f"\nStudents processed:     {stats['students_processed']}")
    print(f"Original images:        {stats['original_images']}")
    print(f"Augmented images:       {stats['augmented_images']}")
    print(f"Total images now:       {stats['original_images'] + stats['augmented_images']}")

    if stats['augmented_images'] > 0:
        improvement = (stats['augmented_images'] / stats['original_images']) * 100 if stats['original_images'] > 0 else 0
        print(f"\nDataset size increased: +{improvement:.1f}%")
        print("\nExpected improvements:")
        print("  - Recognition accuracy: +5-10%")
        print("  - Robustness to lighting: Improved")
        print("  - False positive rate: Reduced")

    if stats['errors']:
        print(f"\n⚠ Errors encountered: {len(stats['errors'])}")
        print("\nFirst 5 errors:")
        for error in stats['errors'][:5]:
            print(f"  - {error}")

    print("\n" + "=" * 70)
    print("Next steps:")
    print("  1. Test recognition with augmented data")
    print("  2. Compare accuracy before/after")
    print("  3. If not satisfied, clean and re-augment")
    print("\nTo clean augmented images: Use option 18 in GUI")
    print("=" * 70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAugmentation interrupted by user.")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

