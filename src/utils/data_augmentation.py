# -*- coding: utf-8 -*-
"""
Data Augmentation Module for Face Recognition
Tăng cường dữ liệu để cải thiện độ chính xác nhận diện
"""
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
from typing import List, Tuple
import random


class FaceDataAugmentation:
    """
    Data Augmentation cho ảnh khuôn mặt
    Tạo thêm ảnh training từ ảnh gốc để tăng độ chính xác
    """

    def __init__(self):
        self.augmentation_methods = [
            'brightness',
            'contrast',
            'blur',
            'noise',
            'flip',
            'rotate',
            'color_jitter'
        ]

    def augment_brightness(self, image: np.ndarray, factor_range: Tuple[float, float] = (0.7, 1.3)) -> np.ndarray:
        """Điều chỉnh độ sáng"""
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        factor = random.uniform(*factor_range)
        enhancer = ImageEnhance.Brightness(pil_img)
        enhanced = enhancer.enhance(factor)
        return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)

    def augment_contrast(self, image: np.ndarray, factor_range: Tuple[float, float] = (0.8, 1.2)) -> np.ndarray:
        """Điều chỉnh độ tương phản"""
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        factor = random.uniform(*factor_range)
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced = enhancer.enhance(factor)
        return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)

    def augment_blur(self, image: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Làm mờ nhẹ (simulate camera blur)"""
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

    def augment_noise(self, image: np.ndarray, noise_factor: float = 0.02) -> np.ndarray:
        """Thêm nhiễu Gaussian (simulate low light)"""
        noise = np.random.randn(*image.shape) * noise_factor * 255
        noisy_image = image + noise
        return np.clip(noisy_image, 0, 255).astype(np.uint8)

    def augment_flip(self, image: np.ndarray) -> np.ndarray:
        """Lật ngang (mirror)"""
        return cv2.flip(image, 1)

    def augment_rotate(self, image: np.ndarray, angle_range: Tuple[int, int] = (-15, 15)) -> np.ndarray:
        """Xoay nhẹ"""
        angle = random.randint(*angle_range)
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)

    def augment_color_jitter(self, image: np.ndarray) -> np.ndarray:
        """Điều chỉnh màu sắc nhẹ"""
        pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        # Random color adjustment
        color_factor = random.uniform(0.9, 1.1)
        enhancer = ImageEnhance.Color(pil_img)
        enhanced = enhancer.enhance(color_factor)
        return cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)

    def augment_image(self, image: np.ndarray, methods: List[str] = None) -> List[np.ndarray]:
        """
        Tạo nhiều phiên bản augmented từ 1 ảnh

        Args:
            image: Ảnh gốc
            methods: Danh sách methods muốn dùng (None = dùng tất cả)

        Returns:
            List các ảnh đã augmented
        """
        if methods is None:
            methods = self.augmentation_methods

        augmented_images = []

        for method in methods:
            try:
                if method == 'brightness':
                    augmented_images.append(self.augment_brightness(image))
                elif method == 'contrast':
                    augmented_images.append(self.augment_contrast(image))
                elif method == 'blur':
                    augmented_images.append(self.augment_blur(image))
                elif method == 'noise':
                    augmented_images.append(self.augment_noise(image))
                elif method == 'flip':
                    augmented_images.append(self.augment_flip(image))
                elif method == 'rotate':
                    # Tạo 2 góc xoay khác nhau
                    augmented_images.append(self.augment_rotate(image, (-10, -5)))
                    augmented_images.append(self.augment_rotate(image, (5, 10)))
                elif method == 'color_jitter':
                    augmented_images.append(self.augment_color_jitter(image))
            except Exception as e:
                print(f"Warning: Failed to apply {method}: {e}")
                continue

        return augmented_images

    def augment_student_images(self, student_dir: str, output_dir: str = None,
                               num_augmented: int = 5) -> int:
        """
        Augment tất cả ảnh của 1 sinh viên

        Args:
            student_dir: Thư mục chứa ảnh sinh viên
            output_dir: Thư mục output (None = ghi vào student_dir)
            num_augmented: Số ảnh augmented muốn tạo từ mỗi ảnh gốc

        Returns:
            Số ảnh đã tạo
        """
        if output_dir is None:
            output_dir = student_dir

        os.makedirs(output_dir, exist_ok=True)

        # Lấy tất cả ảnh trong thư mục
        image_files = [f for f in os.listdir(student_dir)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                      and not f.startswith('aug_')]

        total_created = 0

        for img_file in image_files:
            try:
                # Đọc ảnh
                img_path = os.path.join(student_dir, img_file)
                image = cv2.imread(img_path)

                if image is None:
                    continue

                # Chọn random methods để tạo diversity
                selected_methods = random.sample(
                    self.augmentation_methods,
                    min(num_augmented, len(self.augmentation_methods))
                )

                # Tạo augmented images
                augmented = self.augment_image(image, selected_methods)

                # Lưu ảnh
                base_name = os.path.splitext(img_file)[0]
                for idx, aug_img in enumerate(augmented[:num_augmented]):
                    aug_filename = f"aug_{base_name}_{idx}.jpg"
                    aug_path = os.path.join(output_dir, aug_filename)
                    cv2.imwrite(aug_path, aug_img)
                    total_created += 1

            except Exception as e:
                print(f"Error augmenting {img_file}: {e}")
                continue

        return total_created


class VGGFace2Inspired:
    """
    Áp dụng các kỹ thuật từ VGGFace2 paper
    Không cần download dataset, chỉ áp dụng best practices
    """

    @staticmethod
    def apply_face_alignment(image: np.ndarray) -> np.ndarray:
        """
        Face alignment - căn chỉnh khuôn mặt theo landmark
        Technique từ VGGFace2
        """
        # Detect face
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            # Lấy face đầu tiên
            x, y, w, h = faces[0]

            # Crop và resize về kích thước chuẩn (224x224 như VGGFace2)
            face = image[y:y+h, x:x+w]
            face_resized = cv2.resize(face, (224, 224))

            return face_resized

        return cv2.resize(image, (224, 224))

    @staticmethod
    def apply_histogram_equalization(image: np.ndarray) -> np.ndarray:
        """
        Histogram Equalization - cải thiện contrast
        Technique từ VGGFace2 preprocessing
        """
        # Convert to YCrCb
        ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)

        # Equalize histogram of Y channel
        ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])

        # Convert back to BGR
        return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    @staticmethod
    def apply_photometric_normalization(image: np.ndarray) -> np.ndarray:
        """
        Photometric normalization - chuẩn hóa ánh sáng
        Technique từ VGGFace2
        """
        # Convert to float
        img_float = image.astype(np.float32)

        # Normalize each channel
        for i in range(3):
            channel = img_float[:, :, i]
            mean = np.mean(channel)
            std = np.std(channel)
            if std > 0:
                img_float[:, :, i] = (channel - mean) / std

        # Scale back to 0-255
        img_normalized = ((img_float - img_float.min()) /
                         (img_float.max() - img_float.min()) * 255)

        return img_normalized.astype(np.uint8)

    @staticmethod
    def preprocess_vggface2_style(image: np.ndarray) -> np.ndarray:
        """
        Áp dụng toàn bộ preprocessing pipeline của VGGFace2
        """
        # 1. Face alignment
        aligned = VGGFace2Inspired.apply_face_alignment(image)

        # 2. Histogram equalization
        equalized = VGGFace2Inspired.apply_histogram_equalization(aligned)

        # 3. Photometric normalization
        normalized = VGGFace2Inspired.apply_photometric_normalization(equalized)

        return normalized


def augment_existing_dataset(data_dir: str, augmentation_per_image: int = 5) -> dict:
    """
    Augment toàn bộ dataset hiện có

    Args:
        data_dir: Thư mục chứa data/students
        augmentation_per_image: Số ảnh augmented từ mỗi ảnh gốc

    Returns:
        Dict với thống kê
    """
    augmentor = FaceDataAugmentation()

    stats = {
        'students_processed': 0,
        'original_images': 0,
        'augmented_images': 0,
        'errors': []
    }

    # Duyệt qua tất cả student folders
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} does not exist")
        return stats

    for student_id in os.listdir(data_dir):
        student_dir = os.path.join(data_dir, student_id)

        if not os.path.isdir(student_dir):
            continue

        try:
            # Đếm ảnh gốc
            original_count = len([f for f in os.listdir(student_dir)
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                                 and not f.startswith('aug_')])

            # Augment
            created = augmentor.augment_student_images(
                student_dir,
                num_augmented=augmentation_per_image
            )

            stats['students_processed'] += 1
            stats['original_images'] += original_count
            stats['augmented_images'] += created

            print(f"✓ {student_id}: {original_count} original → +{created} augmented")

        except Exception as e:
            error_msg = f"{student_id}: {str(e)}"
            stats['errors'].append(error_msg)
            print(f"✗ {error_msg}")

    return stats


if __name__ == "__main__":
    # Test augmentation
    print("=" * 60)
    print("Face Data Augmentation - VGGFace2 Inspired")
    print("=" * 60)

    # Example usage
    data_dir = "data/students"

    if os.path.exists(data_dir):
        print(f"\nAugmenting dataset in: {data_dir}")
        print("This will create additional training images...")

        stats = augment_existing_dataset(data_dir, augmentation_per_image=5)

        print("\n" + "=" * 60)
        print("AUGMENTATION COMPLETE")
        print("=" * 60)
        print(f"Students processed: {stats['students_processed']}")
        print(f"Original images: {stats['original_images']}")
        print(f"Augmented images created: {stats['augmented_images']}")
        print(f"Total images now: {stats['original_images'] + stats['augmented_images']}")

        if stats['errors']:
            print(f"\nErrors: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
    else:
        print(f"Error: {data_dir} not found")
        print("Please run this from the project root directory")

