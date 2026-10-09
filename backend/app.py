from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO

import os
import uuid
import base64

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# APP CONFIGURATION
# ============================================================

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "model.pt"
)

import tempfile

UPLOAD_FOLDER = os.path.join(
    tempfile.gettempdir(),
    "polevision_uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading YOLO model...")

model = YOLO(MODEL_PATH)

print("YOLO model loaded successfully!")
print("Classes:", model.names)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "success",
        "message": "Pole Detection API is running",
        "model": "YOLO26n",
        "classes": model.names
    })


# ============================================================
# PREDICTION
# ============================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    try:

        # ----------------------------------------------------
        # Check image
        # ----------------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "status": "error",
                "message": "No image uploaded"
            }), 400

        file = request.files["image"]

        if file.filename == "":
            return jsonify({
                "status": "error",
                "message": "No image selected"
            }), 400


        # ----------------------------------------------------
        # Save uploaded image
        # ----------------------------------------------------

        unique_id = str(uuid.uuid4())

        original_filename = (
            unique_id + "_" + file.filename
        )

        original_path = os.path.join(
            UPLOAD_FOLDER,
            original_filename
        )

        file.save(original_path)


        # ----------------------------------------------------
        # YOLO Prediction
        # ----------------------------------------------------

        results = model.predict(
            source=original_path,
            imgsz=640,
            conf=0.25,
            save=False,
            verbose=False
        )


        result = results[0]


        # ----------------------------------------------------
        # Read original image
        # ----------------------------------------------------

        image = Image.open(original_path).convert("RGB")

        draw = ImageDraw.Draw(image)


        # ----------------------------------------------------
        # Detection information
        # ----------------------------------------------------

        detections = []

        if result.boxes is not None:

            for box in result.boxes:

                class_id = int(box.cls[0])

                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                class_name = model.names[class_id]


                detections.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "confidence": round(
                        confidence * 100,
                        2
                    ),
                    "box": {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2
                    }
                })


                # ------------------------------------------------
                # Draw bounding box
                # ------------------------------------------------

                draw.rectangle(
                    [x1, y1, x2, y2],
                    outline=(0, 220, 120),
                    width=5
                )


                # ------------------------------------------------
                # Label
                # ------------------------------------------------

                label = (
                    f"{class_name} "
                    f"{confidence:.2f}"
                )


                # Calculate label size
                try:

                    font = ImageFont.truetype(
                        "arial.ttf",
                        28
                    )

                except:

                    font = ImageFont.load_default()


                bbox = draw.textbbox(
                    (x1, y1),
                    label,
                    font=font
                )

                label_width = bbox[2] - bbox[0]
                label_height = bbox[3] - bbox[1]


                # Label background

                label_top = max(
                    0,
                    y1 - label_height - 10
                )

                draw.rectangle(
                    [
                        x1,
                        label_top,
                        x1 + label_width + 12,
                        y1
                    ],
                    fill=(0, 220, 120)
                )


                # Label text

                draw.text(
                    (
                        x1 + 6,
                        label_top + 3
                    ),
                    label,
                    fill=(0, 0, 0),
                    font=font
                )


        # ----------------------------------------------------
        # Save annotated image
        # ----------------------------------------------------

        output_filename = (
            unique_id + "_result.jpg"
        )

        output_path = os.path.join(
            UPLOAD_FOLDER,
            output_filename
        )

        image.save(
            output_path,
            quality=95
        )


        # ----------------------------------------------------
        # Convert result image to Base64
        # ----------------------------------------------------

        with open(output_path, "rb") as image_file:

            encoded_image = base64.b64encode(
                image_file.read()
            ).decode("utf-8")


        # ----------------------------------------------------
        # Detection statistics
        # ----------------------------------------------------

        total_detections = len(detections)

        electric_poles = sum(
            1
            for d in detections
            if d["class_id"] == 0
        )

        eleven_kv_poles = sum(
            1
            for d in detections
            if d["class_id"] == 1
        )


        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return jsonify({

            "status": "success",

            "message": "Prediction completed successfully",

            "total_detections": total_detections,

            "electric_poles": electric_poles,

            "eleven_kv_poles": eleven_kv_poles,

            "detections": detections,

            "result_image": (
                "data:image/jpeg;base64,"
                + encoded_image
            )

        })


    except Exception as e:

        print("Prediction error:", e)

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("      POLE DETECTION SERVER")
    print("======================================")
    print("Server: http://127.0.0.1:5000")
    print("======================================\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )