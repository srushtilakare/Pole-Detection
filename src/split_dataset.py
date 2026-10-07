from pathlib import Path
import random
import shutil


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_IMAGE_DIR = PROJECT_ROOT / "dataset" / "raw" / "images"
RAW_LABEL_DIR = PROJECT_ROOT / "dataset" / "raw" / "annotations"

YOLO_DIR = PROJECT_ROOT / "dataset" / "yolo"

YOLO_IMAGE_DIR = YOLO_DIR / "images"
YOLO_LABEL_DIR = YOLO_DIR / "labels"


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

TRAIN_RATIO = 0.70
VAL_RATIO = 0.20
TEST_RATIO = 0.10

RANDOM_SEED = 42

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# --------------------------------------------------
# CHECK RATIOS
# --------------------------------------------------

if abs(
    TRAIN_RATIO + VAL_RATIO + TEST_RATIO - 1.0
) > 1e-6:

    raise ValueError(
        "Train, validation and test ratios "
        "must add up to 1.0"
    )


# --------------------------------------------------
# CREATE DIRECTORIES
# --------------------------------------------------

def create_directories():

    for split in ["train", "val", "test"]:

        (YOLO_IMAGE_DIR / split).mkdir(
            parents=True,
            exist_ok=True
        )

        (YOLO_LABEL_DIR / split).mkdir(
            parents=True,
            exist_ok=True
        )


# --------------------------------------------------
# GET DATASET
# --------------------------------------------------

def get_images():

    return sorted(
        [
            file
            for file in RAW_IMAGE_DIR.iterdir()
            if file.is_file()
            and file.suffix.lower()
            in IMAGE_EXTENSIONS
        ]
    )


# --------------------------------------------------
# SPLIT DATASET
# --------------------------------------------------

def split_dataset(images):

    random.seed(RANDOM_SEED)

    images = images.copy()

    random.shuffle(images)

    total = len(images)

    train_count = int(
        total * TRAIN_RATIO
    )

    val_count = int(
        total * VAL_RATIO
    )

    train_images = images[
        :train_count
    ]

    val_images = images[
        train_count:
        train_count + val_count
    ]

    test_images = images[
        train_count + val_count:
    ]

    return (
        train_images,
        val_images,
        test_images
    )


# --------------------------------------------------
# COPY FILES
# --------------------------------------------------

def copy_split(images, split):

    copied = 0
    skipped = 0

    for image_path in images:

        label_path = (
            RAW_LABEL_DIR /
            f"{image_path.stem}.txt"
        )

        if not label_path.exists():

            print(
                f"WARNING: Missing label for "
                f"{image_path.name}"
            )

            skipped += 1

            continue

        destination_image = (
            YOLO_IMAGE_DIR /
            split /
            image_path.name
        )

        destination_label = (
            YOLO_LABEL_DIR /
            split /
            label_path.name
        )

        shutil.copy2(
            image_path,
            destination_image
        )

        shutil.copy2(
            label_path,
            destination_label
        )

        copied += 1

    return copied, skipped


# --------------------------------------------------
# CREATE data.yaml
# --------------------------------------------------

def create_data_yaml():

    yaml_content = """path: .

train: images/train
val: images/val
test: images/test

names:
  0: electric_pole
  1: 11_kv_electric_pole
"""

    yaml_path = YOLO_DIR / "data.yaml"

    with open(
        yaml_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(yaml_content)

    print(
        f"\nCreated: {yaml_path}"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("=" * 60)
    print("ELECTRIC POLE DATASET SPLITTER")
    print("=" * 60)

    if not RAW_IMAGE_DIR.exists():

        print(
            f"ERROR: Image directory not found:\n"
            f"{RAW_IMAGE_DIR}"
        )

        return

    if not RAW_LABEL_DIR.exists():

        print(
            f"ERROR: Label directory not found:\n"
            f"{RAW_LABEL_DIR}"
        )

        return

    images = get_images()

    print(
        f"\nTotal images found: {len(images)}"
    )

    if not images:

        print("No images found.")

        return

    # Create directories
    create_directories()

    # Split
    (
        train_images,
        val_images,
        test_images
    ) = split_dataset(images)

    print("\nDATASET SPLIT")
    print("-" * 60)

    print(
        f"Train      : {len(train_images)} "
        f"({TRAIN_RATIO * 100:.0f}%)"
    )

    print(
        f"Validation : {len(val_images)} "
        f"({VAL_RATIO * 100:.0f}%)"
    )

    print(
        f"Test       : {len(test_images)} "
        f"({TEST_RATIO * 100:.0f}%)"
    )

    # Copy
    print("\nCOPYING FILES...")
    print("-" * 60)

    train_copied, train_skipped = copy_split(
        train_images,
        "train"
    )

    val_copied, val_skipped = copy_split(
        val_images,
        "val"
    )

    test_copied, test_skipped = copy_split(
        test_images,
        "test"
    )

    print(
        f"Train      : {train_copied} copied, "
        f"{train_skipped} skipped"
    )

    print(
        f"Validation : {val_copied} copied, "
        f"{val_skipped} skipped"
    )

    print(
        f"Test       : {test_copied} copied, "
        f"{test_skipped} skipped"
    )

    # Create YAML
    create_data_yaml()

    print("\n" + "=" * 60)
    print("DATASET SPLIT COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()