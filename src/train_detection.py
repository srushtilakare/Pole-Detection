from ultralytics import YOLO


def main():
    print("Loading YOLO26n pretrained model...")

    model = YOLO("yolo26n.pt")

    print("Starting training...")

    results = model.train(
        data="dataset/yolo/data.yaml",
        epochs=50,
        imgsz=640,
        batch=4,
        device="cpu",
        patience=10,
        project="runs/detect",
        name="pole_yolo26n",
    )

    print("Training completed!")


if __name__ == "__main__":
    main()