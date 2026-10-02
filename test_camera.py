import cv2
import time

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Camera test started.")
print("Press Q to quit.")

previous_time = time.time()

while True:

    success, frame = camera.read()

    if not success:
        print("Camera read failed.")
        break

    current_time = time.time()

    fps = 1.0 / max(
        current_time - previous_time,
        0.0001
    )

    previous_time = current_time

    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    cv2.imshow(
        "Camera Test",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()