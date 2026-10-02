from path_planner import calculate_path


passed = 0
failed = 0


def test_path(
    name,
    left,
    center,
    right,
    expected_direction
):

    global passed
    global failed

    result = calculate_path(
        left,
        center,
        right
    )

    actual_direction = result["direction"]

    if actual_direction == expected_direction:

        passed += 1

        print(
            f"PASS | {name} | "
            f"Expected: {expected_direction} | "
            f"Got: {actual_direction}"
        )

    else:

        failed += 1

        print(
            f"FAIL | {name} | "
            f"Expected: {expected_direction} | "
            f"Got: {actual_direction}"
        )


print()
print("==============================")
print(" PATH PLANNER TEST")
print("==============================")
print()


test_path(
    "Center blocked - equal sides",
    0.0,
    3.0,
    0.0,
    "left"
)

test_path(
    "Center blocked - right safer",
    0.8,
    3.0,
    0.2,
    "right"
)

test_path(
    "Center blocked - left safer",
    0.2,
    3.0,
    0.8,
    "left"
)

test_path(
    "Left blocked",
    2.0,
    0.2,
    0.2,
    "forward"
)

test_path(
    "Right blocked",
    0.2,
    0.2,
    2.0,
    "forward"
)

test_path(
    "Both sides blocked - center clear",
    2.0,
    0.2,
    2.0,
    "forward"
)

test_path(
    "All directions blocked",
    2.0,
    3.0,
    2.0,
    "stop"
)

test_path(
    "Completely clear",
    0.2,
    0.3,
    0.2,
    "forward"
)


print()
print("==============================")
print(f"PASSED: {passed}")
print(f"FAILED: {failed}")
print("==============================")
print()


if failed > 0:

    raise AssertionError(
        f"{failed} path planner test(s) failed."
    )

print("ALL TESTS PASSED")