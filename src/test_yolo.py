from ultralytics import YOLO


def main():

    print("Loading YOLO26n...")

    model = YOLO("yolo26n.pt")

    print("\nModel loaded successfully!")

    model.info()


if __name__ == "__main__":
    main()