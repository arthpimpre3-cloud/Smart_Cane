import cv2
import time

from ocr import read_text


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

print("OCR speed test started.")
print("Point camera at text or any object.")
print("Press Q to quit.")

last_ocr_time = 0
OCR_INTERVAL = 1.0

while True:

    success, frame = camera.read()

    if not success:

        print("Camera error.")
        break

    current_time = time.time()

    if (
        current_time - last_ocr_time
        >= OCR_INTERVAL
    ):

        last_ocr_time = current_time

        start_time = time.time()

        results = read_text(frame)

        ocr_time = (
            time.time() - start_time
        )

        print(
            f"OCR processing time: "
            f"{ocr_time:.2f} seconds"
        )

        if results:

            text = " ".join(
                item["text"]
                for item in results
            )

            print(
                f"Detected text: {text}"
            )

    cv2.imshow(
        "OCR Speed Test",
        frame
    )

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):

        break


camera.release()

cv2.destroyAllWindows()

print("OCR speed test stopped.")