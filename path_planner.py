last_direction = None

CLEAR_THRESHOLD = 0.75

DIRECTION_SWITCH_MARGIN = 0.30


def calculate_path(
    left_risk,
    center_risk,
    right_risk
):

    global last_direction

    left_clear = left_risk < CLEAR_THRESHOLD
    center_clear = center_risk < CLEAR_THRESHOLD
    right_clear = right_risk < CLEAR_THRESHOLD

    # Completely clear
    if left_clear and center_clear and right_clear:

        last_direction = "forward"

        return {
            "direction": "forward",
            "status": "CLEAR",
            "confidence": 1.0
        }

    # Center is blocked
    if not center_clear:

        # Both sides blocked
        if not left_clear and not right_clear:

            last_direction = "stop"

            return {
                "direction": "stop",
                "status": "ALL_BLOCKED",
                "confidence": 1.0
            }

        # Both sides are clear
        if left_clear and right_clear:

            difference = abs(
                left_risk - right_risk
            )

            # Risks are almost equal.
            # Keep previous direction.
            if difference < DIRECTION_SWITCH_MARGIN:

                if last_direction in ["left", "right"]:

                    return {
                        "direction": last_direction,
                        "status": "SAFE_ALTERNATIVE",
                        "confidence": 0.50
                    }

                last_direction = "left"

                return {
                    "direction": "left",
                    "status": "SAFE_ALTERNATIVE",
                    "confidence": 0.50
                }

            # Left is clearly safer
            if left_risk < right_risk:

                last_direction = "left"

                confidence = calculate_confidence(
                    left_risk,
                    right_risk
                )

                return {
                    "direction": "left",
                    "status": "SAFE_ALTERNATIVE",
                    "confidence": confidence
                }

            # Right is clearly safer
            last_direction = "right"

            confidence = calculate_confidence(
                right_risk,
                left_risk
            )

            return {
                "direction": "right",
                "status": "SAFE_ALTERNATIVE",
                "confidence": confidence
            }

        # Only right is clear
        if not left_clear and right_clear:

            last_direction = "right"

            confidence = calculate_confidence(
                right_risk,
                left_risk
            )

            return {
                "direction": "right",
                "status": "SAFE_ALTERNATIVE",
                "confidence": confidence
            }

        # Only left is clear
        if left_clear and not right_clear:

            last_direction = "left"

            confidence = calculate_confidence(
                left_risk,
                right_risk
            )

            return {
                "direction": "left",
                "status": "SAFE_ALTERNATIVE",
                "confidence": confidence
            }

    # Center is clear
    if center_clear:

        last_direction = "forward"

        if not left_clear and right_clear:

            return {
                "direction": "forward",
                "status": "CENTER_CLEAR",
                "confidence": 0.90
            }

        if left_clear and not right_clear:

            return {
                "direction": "forward",
                "status": "CENTER_CLEAR",
                "confidence": 0.90
            }

        if not left_clear and not right_clear:

            return {
                "direction": "forward",
                "status": "CENTER_CLEAR",
                "confidence": 0.80
            }

    last_direction = "stop"

    return {
        "direction": "stop",
        "status": "NO_SAFE_PATH",
        "confidence": 0.0
    }


def calculate_confidence(
    safe_risk,
    blocked_risk
):

    difference = blocked_risk - safe_risk

    confidence = 0.5 + (
        difference / 2.0
    )

    confidence = max(
        0.5,
        min(confidence, 1.0)
    )

    return confidence