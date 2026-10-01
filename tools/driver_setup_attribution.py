from engineering_models import (
    TelemetryFinding,
    DriverSetupAttribution
)


def attribute_issue(
    finding
):

    evidence = (
        finding.evidence
        if finding.evidence
        else {}
    )

    trail_braking = evidence.get(
        "trail_braking_quality",
        0.5
    )

    steering = evidence.get(
        "steering_saturation",
        0.5
    )

    consistency = evidence.get(
        "lap_consistency",
        0.5
    )

    driver_score = 0.0
    setup_score = 0.0

    #
    # Driver Indicators
    #

    if trail_braking < 0.5:
        driver_score += 0.4

    if steering > 0.8:
        driver_score += 0.3

    #
    # Setup Indicators
    #

    if consistency > 0.8:
        setup_score += 0.4

    if finding.confidence > 0.8:
        setup_score += 0.2

    total = (
        driver_score +
        setup_score
    )

    if total == 0:

        return DriverSetupAttribution(

            driver_score=0.5,

            setup_score=0.5,

            confidence=0.25,

            rationale=
                "Insufficient telemetry evidence."
        )

    driver_score /= total
    setup_score /= total

    rationale = (
        "Telemetry indicates a stronger driver influence."
        if driver_score > setup_score
        else
        "Telemetry indicates a stronger setup influence."
    )

    return DriverSetupAttribution(

        driver_score=
            round(
                driver_score,
                2
            ),

        setup_score=
            round(
                setup_score,
                2
            ),

        confidence=
            round(
                finding.confidence,
                2
            ),

        rationale=
            rationale
    )


if __name__ == "__main__":

    finding = TelemetryFinding(

        issue="entry understeer",

        confidence=0.91,

        evidence={

            "trail_braking_quality":
                0.35,

            "steering_saturation":
                0.90,

            "lap_consistency":
                0.80
        }
    )

    result = attribute_issue(
        finding
    )

    print("")
    print(result)
