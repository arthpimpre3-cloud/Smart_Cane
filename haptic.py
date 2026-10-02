import time
import threading

running = True
haptic_thread = None


def motor_left(on):
    if on:
        print("HAPTIC: LEFT MOTOR ON")
    else:
        print("HAPTIC: LEFT MOTOR OFF")


def motor_right(on):
    if on:
        print("HAPTIC: RIGHT MOTOR ON")
    else:
        print("HAPTIC: RIGHT MOTOR OFF")


def all_off():
    motor_left(False)
    motor_right(False)


def caution_pattern():
    motor_left(True)
    motor_right(True)
    time.sleep(0.2)

    all_off()
    time.sleep(0.8)


def danger_pattern():
    motor_left(True)
    motor_right(True)
    time.sleep(0.5)

    all_off()
    time.sleep(0.3)

    motor_left(True)
    motor_right(True)
    time.sleep(0.5)

    all_off()


def move_left_pattern():
    motor_left(True)
    time.sleep(0.25)
    motor_left(False)

    time.sleep(0.25)

    motor_left(True)
    time.sleep(0.25)
    motor_left(False)


def move_right_pattern():
    motor_right(True)
    time.sleep(0.25)
    motor_right(False)

    time.sleep(0.25)

    motor_right(True)
    time.sleep(0.25)
    motor_right(False)


def stop_pattern():
    motor_left(True)
    motor_right(True)
    time.sleep(0.8)

    all_off()
    time.sleep(0.2)


def run_haptic(state):
    if state == "CAUTION":
        caution_pattern()

    elif state == "DANGER":
        danger_pattern()

    elif state == "MOVE_LEFT":
        move_left_pattern()

    elif state == "MOVE_RIGHT":
        move_right_pattern()

    elif state == "STOP":
        stop_pattern()

    else:
        all_off()