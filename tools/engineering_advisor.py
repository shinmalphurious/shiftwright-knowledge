from engineering_models import (
    TelemetryFinding,
    RecommendationPackage
)

from manual_service import (
    SearchContext
)

from knowledge_reasoner import (
    build_recommendations
)


class EngineeringAdvisor:

    def advise(
        self,
        finding,
        context
    ):

        return build_recommendations(
            finding,
            context
        )


_advisor = EngineeringAdvisor()


def advise(
    finding,
    context
):

    return _advisor.advise(
        finding,
        context
    )


if __name__ == "__main__":

    finding = TelemetryFinding(

        issue="entry understeer",

        confidence=0.91,

        corners=[
            "T3",
            "T6"
        ],

        evidence={}
    )

    context = SearchContext(

        vehicle="Porsche 963 GTP",

        manufacturer="Porsche",

        car_class="GTP"
    )

    package = advise(
        finding,
        context
    )

    print("")
    print("=" * 80)
    print("Engineering Advisor")
    print("=" * 80)

    print("")
    print(
        f"Issue: {package.issue}"
    )

    print(
        f"Vehicle: {package.vehicle}"
    )

    print(
        f"Telemetry Confidence: "
        f"{package.telemetry_confidence}"
    )

    print(
        f"Setup Confidence: "
        f"{package.setup_confidence}"
    )

    print("")

    for rec in (
        package.recommendations
    ):

        print(
            f"{rec.lever}"
        )

        print(
            f"  Direction: "
            f"{rec.direction}"
        )

        print(
            f"  Confidence: "
            f"{rec.confidence}"
        )

        print(
            f"  Reason: "
            f"{rec.rationale}"
        )

        print("")
