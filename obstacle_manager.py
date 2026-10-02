from collections import deque


left_risk_history = deque(maxlen=5)
center_risk_history = deque(maxlen=5)
right_risk_history = deque(maxlen=5)


last_safe_direction = None


CLEAR_THRESHOLD = 0.75
DIRECTION_SWITCH_MARGIN = 0.30


def get_position(center_x, frame_width):

    third = frame_width / 3

    if center_x < third:
        return "left"

    if center_x < third * 2:
        return "center"

    return "right"


def get_vision_proximity(
    height,
    frame_height=480
):

    ratio = height / frame_height

    if ratio >= 0.55:
        return "VERY CLOSE"

    if ratio >= 0.35:
        return "CLOSE"

    if ratio >= 0.20:
        return "CAUTION"

    return "FAR"


def get_distance_factor(proximity):

    if proximity == "VERY CLOSE":
        return 3.0

    if proximity == "CLOSE":
        return 2.0

    if proximity == "CAUTION":
        return 1.25

    if proximity == "FAR":
        return 0.5

    return 1.0


def combine_proximity(
    vision_proximity,
    sensor_distance
):

    if sensor_distance is None:
        return vision_proximity

    if sensor_distance <= 0.40:
        sensor_proximity = "VERY CLOSE"

    elif sensor_distance <= 0.80:
        sensor_proximity = "CLOSE"

    elif sensor_distance <= 1.50:
        sensor_proximity = "CAUTION"

    else:
        sensor_proximity = "FAR"

    levels = {
        "FAR": 0,
        "CAUTION": 1,
        "CLOSE": 2,
        "VERY CLOSE": 3
    }

    if levels[sensor_proximity] > levels[vision_proximity]:

        return sensor_proximity

    return vision_proximity


def calculate_object_risk(
    detection,
    frame_width,
    sensor_distance
):

    position = get_position(
        detection["center_x"],
        frame_width
    )

    proximity = get_vision_proximity(
        detection["height"]
    )

    proximity = combine_proximity(
        proximity,
        sensor_distance
    )

    distance_factor = get_distance_factor(
        proximity
    )

    risk = (
        detection["confidence"]
        * distance_factor
    )

    return (
        position,
        proximity,
        risk
    )


def smooth_risks(
    left_risk,
    center_risk,
    right_risk
):

    left_risk_history.append(
        left_risk
    )

    center_risk_history.append(
        center_risk
    )

    right_risk_history.append(
        right_risk
    )

    left_average = (
        sum(left_risk_history)
        / len(left_risk_history)
    )

    center_average = (
        sum(center_risk_history)
        / len(center_risk_history)
    )

    right_average = (
        sum(right_risk_history)
        / len(right_risk_history)
    )

    return (
        left_average,
        center_average,
        right_average
    )


def get_scene_state(
    left_risk,
    center_risk,
    right_risk
):

    left_blocked = (
        left_risk >= CLEAR_THRESHOLD
    )

    center_blocked = (
        center_risk >= CLEAR_THRESHOLD
    )

    right_blocked = (
        right_risk >= CLEAR_THRESHOLD
    )

    if (
        left_blocked
        and center_blocked
        and right_blocked
    ):

        return "ALL_BLOCKED"

    if (
        center_blocked
        and left_blocked
    ):

        return "LEFT_AND_CENTER_BLOCKED"

    if (
        center_blocked
        and right_blocked
    ):

        return "CENTER_AND_RIGHT_BLOCKED"

    if (
        left_blocked
        and right_blocked
    ):

        return "BOTH_SIDES_BLOCKED"

    if center_blocked:
        return "CENTER_BLOCKED"

    if left_blocked:
        return "LEFT_BLOCKED"

    if right_blocked:
        return "RIGHT_BLOCKED"

    return "CLEAR"


def get_safe_direction(
    left_risk,
    center_risk,
    right_risk,
    scene_state
):

    global last_safe_direction

    left_clear = (
        left_risk < CLEAR_THRESHOLD
    )

    center_clear = (
        center_risk < CLEAR_THRESHOLD
    )

    right_clear = (
        right_risk < CLEAR_THRESHOLD
    )

    # Completely blocked
    if scene_state == "ALL_BLOCKED":

        last_safe_direction = "stop"

        return "stop"

    # Center blocked
    if not center_clear:

        # Both sides blocked
        if (
            not left_clear
            and not right_clear
        ):

            last_safe_direction = "stop"

            return "stop"

        # Both sides clear
        if (
            left_clear
            and right_clear
        ):

            difference = abs(
                left_risk - right_risk
            )

            # Keep previous direction
            # when risks are close
            if (
                difference
                < DIRECTION_SWITCH_MARGIN
            ):

                if last_safe_direction in [
                    "left",
                    "right"
                ]:

                    return last_safe_direction

                last_safe_direction = "left"

                return "left"

            if left_risk < right_risk:

                last_safe_direction = "left"

                return "left"

            last_safe_direction = "right"

            return "right"

        # Only right is clear
        if (
            not left_clear
            and right_clear
        ):

            last_safe_direction = "right"

            return "right"

        # Only left is clear
        if (
            left_clear
            and not right_clear
        ):

            last_safe_direction = "left"

            return "left"

    # Center is clear
    if center_clear:

        last_safe_direction = "forward"

        return "forward"

    last_safe_direction = "stop"

    return "stop"


def select_obstacle(
    detections,
    frame_width,
    sensor_distance
):

    if not detections:

        left_risk_history.clear()
        center_risk_history.clear()
        right_risk_history.clear()

        return None

    processed = []

    left_risk = 0.0
    center_risk = 0.0
    right_risk = 0.0

    for detection in detections:

        (
            position,
            proximity,
            risk
        ) = calculate_object_risk(
            detection,
            frame_width,
            sensor_distance
        )

        item = detection.copy()

        item["position"] = position
        item["proximity"] = proximity
        item["risk"] = risk
        item["distance"] = sensor_distance
        item["average_height"] = (
            detection["height"]
        )
        item["frame_width"] = frame_width

        processed.append(item)

        if position == "left":

            left_risk += risk

        elif position == "center":

            center_risk += risk

        elif position == "right":

            right_risk += risk

    (
        left_risk,
        center_risk,
        right_risk
    ) = smooth_risks(
        left_risk,
        center_risk,
        right_risk
    )

    scene_state = get_scene_state(
        left_risk,
        center_risk,
        right_risk
    )

    safe_direction = get_safe_direction(
        left_risk,
        center_risk,
        right_risk,
        scene_state
    )

    for item in processed:

        item["safe_direction"] = (
            safe_direction
        )

        item["scene_state"] = (
            scene_state
        )

        item["left_risk"] = (
            left_risk
        )

        item["center_risk"] = (
            center_risk
        )

        item["right_risk"] = (
            right_risk
        )

        item["left_clear"] = (
            left_risk < CLEAR_THRESHOLD
        )

        item["right_clear"] = (
            right_risk < CLEAR_THRESHOLD
        )

    selected = max(
        processed,
        key=lambda item: item["risk"]
   )

    selected["all_detections"] = processed

    selected["situation_changed"] = True

    return selected