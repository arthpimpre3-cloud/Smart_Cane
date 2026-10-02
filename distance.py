from collections import deque


# Distance history for smoothing
distance_history = deque(maxlen=5)

# Simulated distances for laptop testing
simulated_distances = [
    1.00,
    0.80,
    0.60,
    0.40
]

simulation_index = 0

sensor = None
sensor_available = False


def initialize_sensor():

    global sensor
    global sensor_available

    try:

        import board
        import busio
        import adafruit_vl53l0x

        i2c = busio.I2C(
            board.SCL,
            board.SDA
        )

        sensor = adafruit_vl53l0x.VL53L0X(
            i2c
        )

        sensor_available = True

        print("Distance sensor connected!")

        return True

    except Exception as error:

        sensor_available = False

        print(
            f"Distance sensor not available: {error}"
        )

        print(
            "Using simulated distance."
        )

        return False


def get_raw_distance():

    global simulation_index

    if sensor_available and sensor is not None:

        try:

            distance_mm = sensor.range

            distance_m = distance_mm / 1000.0

            return distance_m

        except Exception as error:

            print(
                f"Distance sensor read error: {error}"
            )

            return None

    distance = simulated_distances[
        simulation_index
    ]

    simulation_index += 1

    if simulation_index >= len(
        simulated_distances
    ):

        simulation_index = (
            len(simulated_distances) - 1
        )

    return distance


def get_distance():

    raw_distance = get_raw_distance()

    if raw_distance is None:

        return None

    distance_history.append(
        raw_distance
    )

    average_distance = (
        sum(distance_history)
        / len(distance_history)
    )

    return average_distance


def get_proximity_from_distance(
    distance
):

    if distance is None:

        return "UNKNOWN"

    if distance <= 0.40:

        return "VERY CLOSE"

    elif distance <= 0.80:

        return "CLOSE"

    elif distance <= 1.50:

        return "CAUTION"

    else:

        return "FAR"


def combine_distance(
    vision_proximity,
    sensor_distance
):

    sensor_proximity = (
        get_proximity_from_distance(
            sensor_distance
        )
    )

    if sensor_proximity == "UNKNOWN":

        return vision_proximity

    if sensor_proximity == "VERY CLOSE":

        return "VERY CLOSE"

    if sensor_proximity == "CLOSE":

        if vision_proximity == "VERY CLOSE":
            return "VERY CLOSE"

        return "CLOSE"

    if sensor_proximity == "CAUTION":

        if vision_proximity == "VERY CLOSE":
            return "VERY CLOSE"

        if vision_proximity == "CLOSE":
            return "CLOSE"

        return "CAUTION"

    return vision_proximity