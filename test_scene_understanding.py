from scene_understanding import (
    describe_detection,
    build_scene,
    create_scene_message
)


def test_single_object():

    detection = {
        "object": "person",
        "position": "center",
        "risk": 3.0
    }

    result = describe_detection(detection)

    assert result == "Person ahead"

    print("PASS | Single center object")


def test_left_object():

    detection = {
        "object": "bicycle",
        "position": "left",
        "risk": 1.0
    }

    result = describe_detection(detection)

    assert result == "Bicycle on your left"

    print("PASS | Left object")


def test_right_object():

    detection = {
        "object": "car",
        "position": "right",
        "risk": 2.0
    }

    result = describe_detection(detection)

    assert result == "Car on your right"

    print("PASS | Right object")


def test_multiple_objects():

    detections = [

        {
            "object": "person",
            "position": "center",
            "risk": 3.0
        },

        {
            "object": "bicycle",
            "position": "right",
            "risk": 1.5
        },

        {
            "object": "chair",
            "position": "left",
            "risk": 0.8
        }
    ]

    scene = build_scene(detections)

    assert scene == [
        "Person ahead",
        "Bicycle on your right",
        "Chair on your left"
    ]

    print("PASS | Multiple objects")


def test_risk_order():

    detections = [

        {
            "object": "bicycle",
            "position": "right",
            "risk": 1.0
        },

        {
            "object": "person",
            "position": "center",
            "risk": 3.0
        }
    ]

    scene = build_scene(detections)

    assert scene[0] == "Person ahead"
    assert scene[1] == "Bicycle on your right"

    print("PASS | Risk ordering")


def test_scene_message():

    detections = [

        {
            "object": "person",
            "position": "center",
            "risk": 3.0
        },

        {
            "object": "bicycle",
            "position": "right",
            "risk": 1.5
        }
    ]

    message = create_scene_message(
        detections
    )

    assert message == (
        "Person ahead. "
        "Bicycle on your right."
    )

    print("PASS | Scene message")


def test_empty_scene():

    result = create_scene_message([])

    assert result is None

    print("PASS | Empty scene")


def test_maximum_three_objects():

    detections = [

        {
            "object": "person",
            "position": "center",
            "risk": 4.0
        },

        {
            "object": "car",
            "position": "left",
            "risk": 3.0
        },

        {
            "object": "bicycle",
            "position": "right",
            "risk": 2.0
        },

        {
            "object": "chair",
            "position": "left",
            "risk": 1.0
        }
    ]

    scene = build_scene(detections)

    message = create_scene_message(
        detections
    )

    assert len(scene) == 4

    assert message.count(".") == 3

    assert "Person ahead" in message
    assert "Car on your left" in message
    assert "Bicycle on your right" in message

    assert "Chair on your left" not in message

    print("PASS | Maximum three spoken objects")


print()
print("==============================")
print(" SCENE UNDERSTANDING TEST")
print("==============================")
print()


test_single_object()
test_left_object()
test_right_object()
test_multiple_objects()
test_risk_order()
test_scene_message()
test_empty_scene()
test_maximum_three_objects()


print()
print("==============================")
print(" ALL TESTS PASSED")
print("==============================")