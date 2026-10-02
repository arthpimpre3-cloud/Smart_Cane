gps_available = False

# Simulated GPS coordinates for laptop testing
SIMULATED_LATITUDE = 18.5204
SIMULATED_LONGITUDE = 73.8567


def initialize_gps():

    global gps_available

    gps_available = False

    print("GPS hardware not connected.")
    print("Using simulated GPS location.")

    return False


def get_location():

    if gps_available:
        # Real GPS code will be added here later
        return None

    return (
        SIMULATED_LATITUDE,
        SIMULATED_LONGITUDE
    )