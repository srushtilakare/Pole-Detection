from pathlib import Path
from collections import Counter


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LABEL_DIR = PROJECT_ROOT / "dataset" / "yolo" / "labels"

CLASS_NAMES = {
    0: "electric_pole",
    1: "11_kv_electric_pole",
}


def count_classes(split):

    split_dir = LABEL_DIR / split

    counts = Counter()

    for label_file in split_dir.glob("*.txt"):

        with open(
            label_file,
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

                counts[class_id] += 1

    return counts


def main():

    print("=" * 60)
    print("CLASS DISTRIBUTION ACROSS DATASET SPLITS")
    print("=" * 60)

    for split in ["train", "val", "test"]:

        counts = count_classes(split)

        print(f"\n{split.upper()}")
        print("-" * 60)

        for class_id, class_name in CLASS_NAMES.items():

            print(
                f"{class_id} - {class_name:<25}: "
                f"{counts[class_id]}"
            )

        print(
            f"Total objects: "
            f"{sum(counts.values())}"
        )


if __name__ == "__main__":
    main()