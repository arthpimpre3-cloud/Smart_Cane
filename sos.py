sos_triggered = False


def trigger_sos(location=None):
    global sos_triggered

    if sos_triggered:
        return

    sos_triggered = True

    if location is not None:
        latitude, longitude = location
        location_text = (
            f"Latitude {latitude:.6f}, "
            f"longitude {longitude:.6f}"
        )
    else:
        location_text = "GPS location not available."

    print()
    print("===================================")
    print("        EMERGENCY SOS TRIGGERED")
    print("===================================")
    print("Emergency assistance requested!")
    print(f"Location: {location_text}")
    print("===================================")
    print()

    from voice import say

    say(
        "Emergency SOS activated. "
        "Please provide assistance."
    )


def reset_sos():
    global sos_triggered
    sos_triggered = False