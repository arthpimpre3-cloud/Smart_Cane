from ultralytics import YOLO


model = YOLO("yolo11n.pt")


TARGET_OBJECTS = {
    "person",
    "car",
    "bus",
    "truck",
    "bicycle",
    "motorcycle",
    "cell phone",
    "chair",
    "laptop",
    "backpack",
    "suitcase",
    "bottle",
    "cup",
    "book",
    "keyboard",
    "mouse",
    "remote",
    "umbrella",
    "handbag",
    "tie"
}


def detect_objects(frame):

    results = model(
    frame,
    imgsz=416,
    verbose=False
  )

    detections = []

    result = results[0]

    if result.boxes is None:
        return detections, result

    for box in result.boxes:

        confidence = float(box.conf[0])

        if confidence < 0.50:
            continue

        class_id = int(box.cls[0])

        object_name = model.names[class_id]

        if object_name not in TARGET_OBJECTS:
            continue

        x1, y1, x2, y2 = box.xyxy[0].tolist()

        width = x2 - x1
        height = y2 - y1

        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        detections.append({
            "object": object_name,
            "confidence": confidence,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": width,
            "height": height,
            "center_x": center_x,
            "center_y": center_y
        })

    return detections, result