last_warning = None
last_haptic_state = None


def get_haptic_state(obstacle):
    if obstacle is None:
        return "CLEAR"

    proximity = obstacle["proximity"]
    scene_state = obstacle.get("scene_state", "CLEAR")
    safe_direction = obstacle.get("safe_direction", "none")

    if proximity == "VERY CLOSE":

        if scene_state == "ALL_BLOCKED":
            return "STOP"

        if scene_state == "CENTER_BLOCKED":
            if safe_direction == "left":
                return "MOVE_LEFT"

            if safe_direction == "right":
                return "MOVE_RIGHT"

            return "STOP"

        if scene_state == "LEFT_AND_CENTER_BLOCKED":
            return "MOVE_RIGHT"

        if scene_state == "CENTER_AND_RIGHT_BLOCKED":
            return "MOVE_LEFT"

        return "DANGER"

    if proximity == "CLOSE":

        if scene_state == "ALL_BLOCKED":
            return "STOP"

        if scene_state == "CENTER_BLOCKED":

            if safe_direction == "left":
                return "MOVE_LEFT"

            if safe_direction == "right":
                return "MOVE_RIGHT"

            return "STOP"

        if scene_state == "LEFT_AND_CENTER_BLOCKED":
            return "MOVE_RIGHT"

        if scene_state == "CENTER_AND_RIGHT_BLOCKED":
            return "MOVE_LEFT"

        return "DANGER"

    if proximity == "CAUTION":
        return "CAUTION"

    return "CLEAR"


def get_haptic_state_changed(state):
    global last_haptic_state

    if state == last_haptic_state:
        return False

    last_haptic_state = state
    return True


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


def create_message(obstacle):
    global last_warning

    if obstacle is None:
        last_warning = None
        return None

    object_name = get_object_name(
        obstacle["object"]
    )

    proximity = obstacle["proximity"]

    safe_direction = obstacle.get(
        "safe_direction",
        "none"
    )

    left_clear = obstacle.get(
        "left_clear",
        False
    )

    right_clear = obstacle.get(
        "right_clear",
        False
    )

    scene_state = obstacle.get(
        "scene_state",
        "CLEAR"
    )

    if proximity == "VERY CLOSE":
        warning = "Danger"

    elif proximity in ["CLOSE", "CAUTION"]:
        warning = "Caution"

    else:
        last_warning = None
        return None

    if scene_state == "ALL_BLOCKED":

        message = (
            f"{warning}. "
            "Path completely blocked. "
            "Stop."
        )

    elif scene_state == "BOTH_SIDES_BLOCKED":

        message = (
            f"{warning}. "
            "Obstacles on both sides. "
            "Continue forward carefully."
        )

    elif scene_state == "LEFT_AND_CENTER_BLOCKED":

        if right_clear:
            message = (
                f"{warning}. "
                "Path blocked on the left. "
                "Move right."
            )
        else:
            message = (
                f"{warning}. "
                "Path blocked. "
                "Stop."
            )

    elif scene_state == "CENTER_AND_RIGHT_BLOCKED":

        if left_clear:
            message = (
                f"{warning}. "
                "Path blocked on the right. "
                "Move left."
            )
        else:
            message = (
                f"{warning}. "
                "Path blocked. "
                "Stop."
            )

    elif scene_state == "CENTER_BLOCKED":

        if safe_direction == "left" and left_clear:
            message = (
                f"{warning}. "
                f"{object_name} ahead. "
                "Move left."
            )

        elif safe_direction == "right" and right_clear:
            message = (
                f"{warning}. "
                f"{object_name} ahead. "
                "Move right."
            )

        else:
            message = (
                f"{warning}. "
                f"{object_name} ahead. "
                "Stop."
            )

    elif scene_state == "LEFT_BLOCKED":

        if right_clear:
            message = (
                f"{warning}. "
                f"{object_name} on your left. "
                "Move right."
            )

        else:
            message = (
                f"{warning}. "
                "Path blocked on the left. "
                "Stop."
            )

    elif scene_state == "RIGHT_BLOCKED":

        if left_clear:
            message = (
                f"{warning}. "
                f"{object_name} on your right. "
                "Move left."
            )

        else:
            message = (
                f"{warning}. "
                "Path blocked on the right. "
                "Stop."
            )

    else:

        if safe_direction == "left" and left_clear:
            message = (
                f"{warning}. "
                "Move left."
            )

        elif safe_direction == "right" and right_clear:
            message = (
                f"{warning}. "
                "Move right."
            )

        elif safe_direction == "forward":
            message = (
                f"{warning}. "
                "Continue forward carefully."
            )

        else:
            message = (
                f"{warning}. "
                "Stop."
            )

    if message == last_warning:
        return None

    last_warning = message

    return message