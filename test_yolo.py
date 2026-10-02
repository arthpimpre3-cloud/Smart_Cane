import cv2
import time
from ultralytics import YOLO

model = YOLO("yolo11n.pt")

camera = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    640
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    480
)

camera.set(
    cv2.CAP_PROP_BUFFERSIZE,
    1
)

print("YOLO test started.")
print("Press Q to quit.")

frame_count = 0
last_time = time.time()

while True:

    success, frame = camera.read()

    if not success:
        print("Camera read failed.")
        break

    frame_count += 1

    if frame_count % 3 == 0:

        start_time = time.time()

        results = model(
            frame,
            imgsz=416,
            verbose=False
        )

        inference_time = (
            time.time() - start_time
        )

        annotated_frame = results[0].plot()

        fps = 1.0 / max(
            time.time() - last_time,
            0.0001
        )

        last_time = time.time()

        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.putText(
            annotated_frame,
            f"YOLO: {inference_time:.2f}s",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

    else:

        annotated_frame = frame

    cv2.imshow(
        "YOLO Test",
        annotated_frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("YOLO test stopped.")