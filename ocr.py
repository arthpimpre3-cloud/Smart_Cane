import cv2
import easyocr


reader = easyocr.Reader(
    ["en"],
    gpu=False
)


MIN_CONFIDENCE = 0.65
MAX_RESULTS = 5
MIN_TEXT_LENGTH = 2

STABILITY_FRAMES = 2

candidate_text = None
candidate_count = 0
stable_text = None


def clean_text(text):

    text = text.strip()

    text = " ".join(
        text.split()
    )

    return text


def is_valid_text(
    text,
    confidence
):

    if confidence < MIN_CONFIDENCE:
        return False

    if len(text) < MIN_TEXT_LENGTH:
        return False

    if "_" in text:
        return False

    return True


def get_box_position(box):

    x_positions = [
        point[0]
        for point in box
    ]

    y_positions = [
        point[1]
        for point in box
    ]

    center_x = (
        sum(x_positions)
        / len(x_positions)
    )

    center_y = (
        sum(y_positions)
        / len(y_positions)
    )

    return (
        center_x,
        center_y
    )


def read_raw_text(frame):

    try:

        # Reduce image size before OCR
        small_frame = cv2.resize(
            frame,
            None,
            fx=0.5,
            fy=0.5,
            interpolation=cv2.INTER_AREA
        )

        results = reader.readtext(
            small_frame,
            detail=1
        )

        detected_text = []

        seen_text = set()

        for result in results:

            confidence = float(
                result[2]
            )

            text = clean_text(
                result[1]
            )

            box = result[0]

            if not is_valid_text(
                text,
                confidence
            ):
                continue

            text_key = text.lower()

            if text_key in seen_text:
                continue

            seen_text.add(
                text_key
            )

            center_x, center_y = (
                get_box_position(box)
            )

            detected_text.append({

                "text": text,

                "confidence":
                    confidence,

                "box": box,

                "center_x":
                    center_x,

                "center_y":
                    center_y
            })


        detected_text = sorted(
            detected_text,
            key=lambda item: (
                item["center_y"],
                item["center_x"]
            )
        )


        return detected_text[
            :MAX_RESULTS
        ]


    except Exception as error:

        print(
            f"OCR error: {error}"
        )

        return []


def texts_are_similar(
    text1,
    text2
):

    words1 = set(
        text1.lower().split()
    )

    words2 = set(
        text2.lower().split()
    )

    if not words1 or not words2:

        return False


    common_words = (
        words1.intersection(
            words2
        )
    )


    similarity = (
        len(common_words)
        /
        max(
            len(words1),
            len(words2)
        )
    )


    return similarity >= 0.60


def read_text(frame):

    global candidate_text
    global candidate_count
    global stable_text


    results = read_raw_text(
        frame
    )


    if not results:

        candidate_text = None

        candidate_count = 0

        return []


    current_text = " ".join(

        item["text"].lower()

        for item in results

    )


    if current_text == stable_text:

        return []


    if (
        candidate_text is not None
        and
        texts_are_similar(
            current_text,
            candidate_text
        )
    ):

        candidate_count += 1

    else:

        candidate_text = (
            current_text
        )

        candidate_count = 1


    print(
        f"OCR candidate "
        f"{candidate_count}/"
        f"{STABILITY_FRAMES}: "
        f"{current_text}"
    )


    if (
        candidate_count
        >= STABILITY_FRAMES
    ):

        stable_text = (
            current_text
        )

        candidate_text = None

        candidate_count = 0

        print(
            f"OCR STABLE: "
            f"{current_text}"
        )

        return results


    return []