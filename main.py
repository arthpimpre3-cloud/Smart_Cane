import cv2
import time
import threading

from camera import get_frame, release_camera
from object_detection import detect_objects
from obstacle_manager import select_obstacle
from path_planner import calculate_path
from haptic import run_haptic

from voice import (
    say,
    stop_voice,
    is_speaking
)

from ocr import read_text

from distance import (
    initialize_sensor,
    get_distance
)

import sos

from gps import (
    initialize_gps,
    get_location
)

from scene_understanding import (
    create_scene_message
)


print("===================================")
print(" VisionGuide Smart Cane Starting ")
print("===================================")


sensor_available = initialize_sensor()
gps_available = initialize_gps()


# =================================
# GLOBAL STATE
# =================================

running = True

state_lock = threading.Lock()

current_haptic_state = "CLEAR"

latest_obstacle = None
latest_path = None

latest_detections = []

last_scene_message = None
last_voice_message = None

latest_ocr_message = None


# =================================
# PERFORMANCE SETTINGS
# =================================

YOLO_SKIP = 3


# =================================
# OCR CONTROL
# =================================

ocr_requested = False
ocr_processing = False

ocr_lock = threading.Lock()


# =================================
# STATUS OVERLAY
# =================================

def draw_status_overlay(
    frame,
    gps_available,
    sensor_available,
    haptic_state
):

    overlay = frame.copy()

    panel_width = 300
    panel_height = 210

    cv2.rectangle(
        overlay,
        (15, 15),
        (
            15 + panel_width,
            15 + panel_height
        ),
        (0, 0, 0),
        -1
    )

    frame = cv2.addWeighted(
        overlay,
        0.70,
        frame,
        0.30,
        0
    )

    gps_status = (
        "CONNECTED"
        if gps_available
        else "SIMULATED"
    )

    distance_status = (
        "CONNECTED"
        if sensor_available
        else "SIMULATED"
    )

    if haptic_state == "CLEAR":

        haptic_color = (
            180,
            255,
            180
        )

    elif haptic_state == "CAUTION":

        haptic_color = (
            0,
            255,
            255
        )

    elif haptic_state in [
        "DANGER",
        "STOP"
    ]:

        haptic_color = (
            0,
            0,
            255
        )

    else:

        haptic_color = (
            0,
            255,
            0
        )

    sos_status = (
        "ACTIVE"
        if sos.sos_triggered
        else "READY"
    )

    sos_color = (
        (0, 0, 255)
        if sos.sos_triggered
        else (0, 255, 0)
    )

    cv2.putText(
        frame,
        "VISIONGUIDE",
        (30, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"GPS       : {gps_status}",
        (30, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        f"DISTANCE  : {distance_status}",
        (30, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        f"HAPTIC    : {haptic_state}",
        (30, 125),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        haptic_color,
        2
    )

    cv2.putText(
        frame,
        f"SOS       : {sos_status}",
        (30, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        sos_color,
        2
    )

    cv2.putText(
        frame,
        "O: READ TEXT",
        (30, 175),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

    cv2.putText(
        frame,
        "S: SOS   R: RESET   Q: QUIT",
        (30, 198),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (200, 200, 200),
        1
    )

    return frame


# =================================
# DRAW DETECTIONS
# =================================

def draw_detections(
    frame,
    detections
):

    for detection in detections:

        x1 = int(
            detection["x1"]
        )

        y1 = int(
            detection["y1"]
        )

        x2 = int(
            detection["x2"]
        )

        y2 = int(
            detection["y2"]
        )

        object_name = (
            detection["object"]
        )

        confidence = (
            detection["confidence"]
        )

        position = (
            detection["position"]
        )

        label = (
            f"{object_name} "
            f"{confidence:.2f} "
            f"{position}"
        )

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )

        cv2.putText(
            frame,
            label,
            (x1, max(y1 - 8, 20)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 0, 0),
            2
        )

    return frame


# =================================
# PLANNER HAPTIC
# =================================

def get_planner_haptic_state(
    path
):

    if path is None:
        return "CLEAR"

    direction = path["direction"]

    if direction == "left":
        return "MOVE_LEFT"

    if direction == "right":
        return "MOVE_RIGHT"

    if direction == "stop":
        return "STOP"

    if direction == "forward":
        return "CLEAR"

    return "CLEAR"


# =================================
# PLANNER VOICE
# =================================

def create_planner_voice(
    path,
    obstacle
):

    if path is None or obstacle is None:
        return None

    direction = path["direction"]

    status = path["status"]

    object_name = obstacle["object"]

    object_names = {
        "person": "Person",
        "car": "Car",
        "bus": "Bus",
        "truck": "Truck",
        "bicycle": "Bicycle",
        "motorcycle": "Motorcycle",
        "cell phone": "Mobile phone",
        "chair": "Chair",
        "laptop": "Laptop",
        "backpack": "Backpack",
        "suitcase": "Suitcase",
        "bottle": "Bottle",
        "cup": "Cup",
        "book": "Book",
        "keyboard": "Keyboard",
        "mouse": "Mouse",
        "remote": "Remote",
        "umbrella": "Umbrella",
        "handbag": "Handbag",
        "tie": "Tie"
    }

    object_name = object_names.get(
        object_name,
        object_name.capitalize()
    )

    if direction == "left":

        return (
            f"Danger. "
            f"{object_name} ahead. "
            "Move left."
        )

    if direction == "right":

        return (
            f"Danger. "
            f"{object_name} ahead. "
            "Move right."
        )

    if direction == "stop":

        if status == "ALL_BLOCKED":

            return (
                "Danger. "
                "Path completely blocked. "
                "Stop."
            )

        return (
            f"Danger. "
            f"{object_name} ahead. "
            "Stop."
        )

    return None


# =================================
# OCR MESSAGE
# =================================

def create_ocr_message(
    ocr_results
):

    if not ocr_results:
        return None

    text_parts = []

    for item in ocr_results:

        text = item["text"].strip()

        if text:
            text_parts.append(text)

    if not text_parts:
        return None

    return " ".join(
        text_parts
    )


# =================================
# HAPTIC WORKER
# =================================

def run_haptic_async(
    state
):

    if not running:
        return

    try:

        run_haptic(state)

    except Exception as error:

        print(
            f"Haptic error: {error}"
        )


def start_haptic(
    state
):

    thread = threading.Thread(
        target=run_haptic_async,
        args=(state,),
        daemon=True
    )

    thread.start()


# =================================
# OCR WORKER
# =================================

def ocr_worker():

    global running
    global ocr_requested
    global ocr_processing
    global latest_ocr_message

    while running:

        with ocr_lock:

            requested = ocr_requested

            if requested:

                ocr_requested = False

                ocr_processing = True

        if not requested:

            time.sleep(0.02)

            continue


        print()
        print(
            "OCR: Reading text..."
        )

        frame = get_frame()

        if frame is None:

            with ocr_lock:
                ocr_processing = False

            continue


        start_time = time.time()

        try:

            results = read_text(
                frame
            )

            ocr_message = (
                create_ocr_message(
                    results
                )
            )

            processing_time = (
                time.time()
                - start_time
            )

            print(
                f"OCR processing time: "
                f"{processing_time:.2f} seconds"
            )


            if ocr_message is not None:

                print(
                    f"OCR Result: "
                    f"{ocr_message}"
                )

                latest_ocr_message = (
                    ocr_message
                )

                # ---------------------------------
                # SAFETY PRIORITY
                # ---------------------------------

                with state_lock:

                    obstacle = (
                        latest_obstacle
                    )

                    path = latest_path


                obstacle_voice = (
                    create_planner_voice(
                        path,
                        obstacle
                    )
                )


                if obstacle_voice is not None:

                    print(
                        "OCR voice skipped "
                        "because obstacle "
                        "warning has priority."
                    )

                elif not is_speaking():

                    print(
                        "OCR Voice:",
                        ocr_message
                    )

                    say(
                        ocr_message
                    )

            else:

                latest_ocr_message = None

                print(
                    "OCR: No stable text found."
                )


        except Exception as error:

            print(
                f"OCR error: "
                f"{error}"
            )


        with ocr_lock:

            ocr_processing = False


# =================================
# AI WORKER
# =================================

def ai_worker():

    global running
    global current_haptic_state
    global latest_obstacle
    global latest_path
    global latest_detections
    global last_scene_message
    global last_voice_message

    local_frame_count = 0

    while running:

        frame = get_frame()

        if frame is None:

            time.sleep(0.01)

            continue


        local_frame_count += 1


        # =================================
        # YOLO FRAME SKIPPING
        # =================================

        if (
            local_frame_count
            % YOLO_SKIP
            != 0
        ):

            time.sleep(0.001)

            continue


        # =================================
        # YOLO
        # =================================

        try:

            detections, result = (
                detect_objects(frame)
            )

        except Exception as error:

            print(
                f"YOLO error: "
                f"{error}"
            )

            continue


        # =================================
        # DISTANCE
        # =================================

        try:

            sensor_distance = (
                get_distance()
            )

        except Exception as error:

            print(
                f"Distance error: "
                f"{error}"
            )

            sensor_distance = None


        # =================================
        # OBSTACLE MANAGER
        # =================================

        obstacle = select_obstacle(
            detections,
            frame.shape[1],
            sensor_distance
        )


        with state_lock:

            latest_obstacle = (
                obstacle
            )

            if obstacle is not None:

                latest_detections = (
                    obstacle.get(
                        "all_detections",
                        []
                    )
               )

            else:

                latest_detections = []


        # =================================
        # SCENE UNDERSTANDING
        # =================================

        scene_detections = []

        if obstacle is not None:

            scene_detections = (
                obstacle.get(
                    "all_detections",
                    []
                )
            )

        scene_message = (
            create_scene_message(
                scene_detections
            )
        )


        if (
            scene_message
            != last_scene_message
        ):

            last_scene_message = (
                scene_message
            )

            if scene_message is not None:

                print(
                    f"Scene: "
                    f"{scene_message}"
                )


        # =================================
        # PATH PLANNER
        # =================================

        path = None

        if obstacle is not None:

            path = calculate_path(
                obstacle["left_risk"],
                obstacle["center_risk"],
                obstacle["right_risk"]
            )

            print(
                f"Path Planner: "
                f"{path['direction']} | "
                f"Status: "
                f"{path['status']} | "
                f"Confidence: "
                f"{path['confidence']:.2f}"
            )


        with state_lock:

            latest_path = path


        # =================================
        # HAPTIC
        # =================================

        planner_haptic_state = (
            get_planner_haptic_state(
                path
            )
        )

        should_start_haptic = False


        with state_lock:

            if (
                planner_haptic_state
                != current_haptic_state
            ):

                current_haptic_state = (
                    planner_haptic_state
                )

                should_start_haptic = True


        if should_start_haptic:

            print(
                "Haptic:",
                planner_haptic_state
            )

            start_haptic(
                planner_haptic_state
            )


        # =================================
        # OBSTACLE VOICE
        # =================================

        obstacle_voice = (
            create_planner_voice(
                path,
                obstacle
            )
        )


        if obstacle_voice is not None:

            if (
                obstacle_voice
                != last_voice_message
            ):

                last_voice_message = (
                    obstacle_voice
                )

                print(
                    "Speaking:",
                    obstacle_voice
                )

                say(
                    obstacle_voice
                )


        # =================================
        # OBSTACLE INFORMATION
        # =================================

        if obstacle is not None:

            distance_text = (
                f"{obstacle['distance']:.2f} m"
                if obstacle["distance"]
                is not None
                else "N/A"
            )

            print(
                f"Detected: "
                f"{obstacle['object']} | "
                f"Confidence: "
                f"{obstacle['confidence']:.2f} | "
                f"Position: "
                f"{obstacle['position']} | "
                f"Proximity: "
                f"{obstacle['proximity']} | "
                f"Distance: "
                f"{distance_text} | "
                f"Average Height: "
                f"{obstacle['average_height']:.0f}"
            )

            print(
                f"Safe Direction: "
                f"{obstacle['safe_direction']} | "
                f"Left Risk: "
                f"{obstacle['left_risk']:.0f} | "
                f"Center Risk: "
                f"{obstacle['center_risk']:.0f} | "
                f"Right Risk: "
                f"{obstacle['right_risk']:.0f}"
            )


        time.sleep(0.001)


# =================================
# START WORKERS
# =================================

ai_thread = threading.Thread(
    target=ai_worker,
    daemon=True
)

ai_thread.start()


ocr_thread = threading.Thread(
    target=ocr_worker,
    daemon=True
)

ocr_thread.start()


# =================================
# MAIN CAMERA LOOP
# =================================

try:

    while True:

        frame = get_frame()

        if frame is None:

            time.sleep(0.01)

            continue


        # =================================
        # GET CURRENT STATE
        # =================================

        with state_lock:

            haptic_state = (
                current_haptic_state
            )

            detections = (
                latest_detections.copy()
            )


        # =================================
        # DRAW DETECTIONS
        # =================================

        display_frame = frame.copy()

        display_frame = (
            draw_detections(
                display_frame,
                detections
            )
        )


        # =================================
        # STATUS OVERLAY
        # =================================

        display_frame = (
            draw_status_overlay(
                display_frame,
                gps_available,
                sensor_available,
                haptic_state
            )
        )


        # =================================
        # SHOW CAMERA
        # =================================

        cv2.imshow(
            "VisionGuide Smart Cane",
            display_frame
        )


        # =================================
        # KEYBOARD
        # =================================

        key = (
            cv2.waitKey(1)
            & 0xFF
        )


        # =================================
        # OCR
        # =================================

        if key == ord("o"):

            with ocr_lock:

                if not ocr_processing:

                    ocr_requested = True

                    print(
                        "OCR requested."
                    )

                else:

                    print(
                        "OCR is already "
                        "processing."
                    )


        # =================================
        # SOS
        # =================================

        elif key == ord("s"):

            location = get_location()

            sos.trigger_sos(
                location
            )


        # =================================
        # RESET SOS
        # =================================

        elif key == ord("r"):

            sos.reset_sos()

            print(
                "SOS reset."
            )


        # =================================
        # QUIT
        # =================================

        elif key == ord("q"):

            break


finally:

    running = False

    time.sleep(0.2)

    release_camera()

    cv2.destroyAllWindows()

    stop_voice()

    print(
        "VisionGuide Smart Cane Stopped."
    )