import cv2
import threading
import time


camera = None
running = False

latest_frame = None
frame_lock = threading.Lock()

camera_thread = None


def camera_worker():
    global latest_frame
    global running

    while running:

        success, frame = camera.read()

        if not success:
            time.sleep(0.01)
            continue

        with frame_lock:
            latest_frame = frame


def initialize_camera():

    global camera
    global running
    global camera_thread

    camera = cv2.VideoCapture(
        0,
        cv2.CAP_DSHOW
    )

    if not camera.isOpened():

        print("Camera could not be opened!")

        return False

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

    print("Camera connected!")

    running = True

    camera_thread = threading.Thread(
        target=camera_worker,
        daemon=True
    )

    camera_thread.start()

    return True


def get_frame():

    global latest_frame

    with frame_lock:

        if latest_frame is None:
            return None

        return latest_frame.copy()


def release_camera():

    global running
    global camera
    global camera_thread

    running = False

    if camera_thread is not None:

        camera_thread.join(
            timeout=1
        )

    if camera is not None:

        camera.release()

        camera = None


initialize_camera()