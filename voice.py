import threading
import queue
import pythoncom
import pyttsx3


speech_queue = queue.Queue(maxsize=1)

running = True
voice_thread = None

speaking = False
speaking_lock = threading.Lock()


def speech_worker():

    global running
    global speaking

    pythoncom.CoInitialize()

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        160
    )

    engine.setProperty(
        "volume",
        1.0
    )

    while running:

        try:

            message = speech_queue.get(
                timeout=0.1
            )

        except queue.Empty:

            continue

        if message is None:
            break

        try:

            with speaking_lock:
                speaking = True

            print(
                f"Voice: {message}"
            )

            engine.say(
                message
            )

            engine.runAndWait()

        except Exception as error:

            print(
                f"Voice error: {error}"
            )

        finally:

            with speaking_lock:
                speaking = False

    try:

        engine.stop()

    except Exception:

        pass

    pythoncom.CoUninitialize()


def start_voice():

    global voice_thread
    global running

    running = True

    voice_thread = threading.Thread(
        target=speech_worker,
        daemon=True
    )

    voice_thread.start()


def is_speaking():

    with speaking_lock:
        return speaking


def say(message):

    if message is None or not running:
        return

    try:

        while True:

            speech_queue.get_nowait()

    except queue.Empty:

        pass

    try:

        speech_queue.put_nowait(
            message
        )

    except queue.Full:

        pass


def stop_current_speech():

    try:

        while True:

            speech_queue.get_nowait()

    except queue.Empty:

        pass


def stop_voice():

    global running

    running = False

    stop_current_speech()

    try:

        speech_queue.put_nowait(
            None
        )

    except queue.Full:

        pass

    if voice_thread is not None:

        voice_thread.join(
            timeout=2
        )


start_voice()