from pathlib import Path
from collections import Counter


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Dataset paths
IMAGE_DIR = PROJECT_ROOT / "dataset" / "raw" / "images"
LABEL_DIR = PROJECT_ROOT / "dataset" / "raw" / "annotations"


# Your dataset classes
CLASS_NAMES = {
    0: "electric_pole",
    1: "11_kv_electric_pole",
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def main():

    print("=" * 60)
    print("ELECTRIC POLE DATASET VALIDATION")
    print("=" * 60)

    # Check folders
    if not IMAGE_DIR.exists():
        print(f"\nERROR: Image folder not found:")
        print(IMAGE_DIR)
        return

    if not LABEL_DIR.exists():
        print(f"\nERROR: Annotation folder not found:")
        print(LABEL_DIR)
        return

    # Find images
    images = {
        file.stem: file
        for file in IMAGE_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() in IMAGE_EXTENSIONS
    }

    # Find annotations
    labels = {
        file.stem: file
        for file in LABEL_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".txt"
    }

    # Dataset size
    print("\nDATASET SIZE")
    print("-" * 60)

    print(f"Images       : {len(images)}")
    print(f"Annotations  : {len(labels)}")

    # Check matching filenames
    missing_labels = set(images) - set(labels)
    missing_images = set(labels) - set(images)

    print("\nFILE MATCHING")
    print("-" * 60)

    print(f"Images without annotations : {len(missing_labels)}")
    print(f"Annotations without images : {len(missing_images)}")

    # Annotation validation
    class_counts = Counter()
    invalid_annotations = []

    for label_file in labels.values():

        with open(label_file, "r", encoding="utf-8") as file:

            for line_number, line in enumerate(file, start=1):

                line = line.strip()

                if not line:
                    continue

                values = line.split()

                # YOLO detection format:
                # class x_center y_center width height
                if len(values) != 5:

                    invalid_annotations.append(
                        f"{label_file.name}:{line_number} "
                        f"Expected 5 values, got {len(values)}"
                    )

                    continue

                try:

                    class_id = int(values[0])

                    coordinates = [
                        float(value)
                        for value in values[1:]
                    ]

                except ValueError:

                    invalid_annotations.append(
                        f"{label_file.name}:{line_number} "
                        "Contains invalid numbers"
                    )

                    continue

                # Check class
                if class_id not in CLASS_NAMES:

                    invalid_annotations.append(
                        f"{label_file.name}:{line_number} "
                        f"Unknown class ID: {class_id}"
                    )

                # Check normalized coordinates
                if not all(
                    0 <= value <= 1
                    for value in coordinates
                ):

                    invalid_annotations.append(
                        f"{label_file.name}:{line_number} "
                        "Coordinates must be between 0 and 1"
                    )

                class_counts[class_id] += 1

    # Class distribution
    print("\nCLASS DISTRIBUTION")
    print("-" * 60)

    for class_id, class_name in CLASS_NAMES.items():

        print(
            f"Class {class_id} - {class_name}: "
            f"{class_counts[class_id]} objects"
        )

    # Invalid annotations
    print("\nANNOTATION VALIDATION")
    print("-" * 60)

    if invalid_annotations:

        print(
            f"Invalid annotation entries: "
            f"{len(invalid_annotations)}"
        )

        print("\nFirst few problems:")

        for error in invalid_annotations[:20]:
            print(error)

    else:

        print("All annotations passed validation.")

    # Final result
    print("\n" + "=" * 60)

    if (
        len(images) == len(labels)
        and not missing_labels
        and not missing_images
        and not invalid_annotations
    ):

        print("DATASET STATUS: READY")

    else:

        print("DATASET STATUS: NEEDS ATTENTION")

    print("=" * 60)


if __name__ == "__main__":
    main()