from engineering_models import (
    TelemetryFinding
)


def clamp(
    value,
    minimum=0.0,
    maximum=1.0
):

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


def score_trail_braking(

    brake_release_delta

):
    """
    Input:

    0.0 = identical to reference

    1.0 = terrible match

    """

    return clamp(
        1.0 -
        brake_release_delta
    )


def score_steering_saturation(

    driver_peak_steering,

    reference_peak_steering
):

    if reference_peak_steering <= 0:
        return 0.5

    ratio = (
        driver_peak_steering /
        reference_peak_steering
    )

    score = (
        ratio - 1.0
    ) * 2.0

    return clamp(
        score
    )


def score_rotation(

    driver_yaw_rate,

    reference_yaw_rate
):

    if reference_yaw_rate <= 0:
        return 0.5

    return clamp(
        driver_yaw_rate /
        reference_yaw_rate
    )


def score_minimum_speed_delta(

    driver_min_speed,

    reference_min_speed
):

    if reference_min_speed <= 0:
        return 0.0

    delta = (

        reference_min_speed -
        driver_min_speed

    ) / reference_min_speed

    return clamp(
        delta
    )


def score_consistency(

    standard_deviation,

    expected_max_stddev=5.0
):

    normalized = (
        standard_deviation /
        expected_max_stddev
    )

    return clamp(
        1.0 - normalized
    )


def build_entry_understeer_finding(

    trail_braking_quality,

    steering_saturation,

    rotation_score,

    lap_consistency,

    minimum_speed_delta
):

    confidence = (

        steering_saturation * 0.35 +

        (1.0 - rotation_score) * 0.35 +

        minimum_speed_delta * 0.20 +

        lap_consistency * 0.10

    )

    confidence = clamp(
        confidence
    )

    return TelemetryFinding(

        issue="entry understeer",

        confidence=round(
            confidence,
            2
        ),

        evidence={

            "trail_braking_quality":
                trail_braking_quality,

            "steering_saturation":
                steering_saturation,

            "rotation_score":
                rotation_score,

            "lap_consistency":
                lap_consistency,

            "minimum_speed_delta":
                minimum_speed_delta
        }
    )


if __name__ == "__main__":

    trail_braking = (
        score_trail_braking(
            0.15
        )
    )

    steering = (
        score_steering_saturation(

            driver_peak_steering=44,

            reference_peak_steering=32
        )
    )

    rotation = (
        score_rotation(

            driver_yaw_rate=11,

            reference_yaw_rate=18
        )
    )

    minimum_speed = (
        score_minimum_speed_delta(

            driver_min_speed=85,

            reference_min_speed=92
        )
    )

    consistency = (
        score_consistency(
            0.8
        )
    )

    finding = (
        build_entry_understeer_finding(

            trail_braking,

            steering,

            rotation,

            consistency,

            minimum_speed
        )
    )

    print("")
    print("=" * 80)
    print("Telemetry Finding")
    print("=" * 80)
    print("")

    print(
        finding
    )