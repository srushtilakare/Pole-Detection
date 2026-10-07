from pathlib import Path
import random

import cv2
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent.parent

IMAGE_DIR = PROJECT_ROOT / "dataset" / "raw" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "raw" / "annotations"

CLASS_NAMES = {
    0: "electric_pole",
    1: "11_kv_electric_pole",
}

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


def draw_annotations(image_path, label_path):

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            f"Could not read image: {image_path}"
        )

    # OpenCV uses BGR.
    # Matplotlib expects RGB.
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    height, width = image.shape[:2]

    with open(
        label_path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            values = line.split()

            if len(values) != 5:
                continue

            class_id = int(values[0])

            x_center = float(values[1])
            y_center = float(values[2])
            box_width = float(values[3])
            box_height = float(values[4])

            # Convert normalized YOLO coordinates
            # into pixel coordinates.

            x_center *= width
            y_center *= height

            box_width *= width
            box_height *= height

            x1 = int(
                x_center - box_width / 2
            )

            y1 = int(
                y_center - box_height / 2
            )

            x2 = int(
                x_center + box_width / 2
            )

            y2 = int(
                y_center + box_height / 2
            )

            # Keep box inside image
            x1 = max(0, x1)
            y1 = max(0, y1)

            x2 = min(width - 1, x2)
            y2 = min(height - 1, y2)

            # Draw bounding box
            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                3
            )

            class_name = CLASS_NAMES.get(
                class_id,
                f"class_{class_id}"
            )

            # Draw class name
            cv2.putText(
                image,
                class_name,
                (x1, max(25, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2
            )

    return image


def main():

    images = [
        file
        for file in IMAGE_DIR.iterdir()
        if file.suffix.lower()
        in IMAGE_EXTENSIONS
    ]

    if not images:

        print("No images found.")

        return

    # Select 9 random images
    sample_size = min(9, len(images))

    selected_images = random.sample(
        images,
        sample_size
    )

    plt.figure(
        figsize=(15, 12)
    )

    for index, image_path in enumerate(
        selected_images
    ):

        label_path = (
            LABEL_DIR /
            f"{image_path.stem}.txt"
        )

        if not label_path.exists():

            print(
                f"Missing label: "
                f"{image_path.name}"
            )

            continue

        image = draw_annotations(
            image_path,
            label_path
        )

        plt.subplot(
            3,
            3,
            index + 1
        )

        plt.imshow(image)

        plt.title(
            image_path.name,
            fontsize=8
        )

        plt.axis("off")

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    main()