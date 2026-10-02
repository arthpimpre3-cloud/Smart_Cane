STABILITY_FRAMES = 3

candidate_scene = None
candidate_count = 0
stable_scene = None


def get_object_name(object_name):

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

    return object_names.get(
        object_name,
        object_name.capitalize()
    )


def describe_detection(detection):

    object_name = get_object_name(
        detection["object"]
    )

    position = detection["position"]

    if position == "left":
        position_text = "on your left"

    elif position == "right":
        position_text = "on your right"

    else:
        position_text = "ahead"

    return f"{object_name} {position_text}"


def build_scene(detections):

    if not detections:
        return []

    sorted_detections = sorted(
        detections,
        key=lambda item: item["risk"],
        reverse=True
    )

    scene = []
    seen = set()

    for detection in sorted_detections:

        object_name = detection["object"]
        position = detection["position"]

        key = (
            object_name,
            position
        )

        if key in seen:
            continue

        seen.add(key)

        description = describe_detection(
            detection
        )

        scene.append(description)

    return scene


def create_scene_message(detections):

    global candidate_scene
    global candidate_count
    global stable_scene

    scene = build_scene(detections)

    current_scene = tuple(scene)

    if current_scene == stable_scene:

        candidate_scene = None
        candidate_count = 0

        if not scene:
            return None

        return create_message_from_scene(
            scene
        )

    if current_scene == candidate_scene:

        candidate_count += 1

    else:

        candidate_scene = current_scene
        candidate_count = 1

    if candidate_count >= STABILITY_FRAMES:

        stable_scene = current_scene
        candidate_scene = None
        candidate_count = 0

    if stable_scene is None:

        return None

    if not stable_scene:

        return None

    return create_message_from_scene(
        list(stable_scene)
    )


def create_message_from_scene(scene):

    if not scene:
        return None

    if len(scene) == 1:

        return scene[0] + "."

    if len(scene) == 2:

        return (
            scene[0]
            + ". "
            + scene[1]
            + "."
        )

    message = ""

    for item in scene[:3]:

        if message:
            message += ". "

        message += item

    message += "."

    return message