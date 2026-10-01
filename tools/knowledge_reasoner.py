from manual_service import SearchContext
from knowledge_builder import build_knowledge
from knowledge_ranker import rank_setup_levers

from engineering_models import (
    TelemetryFinding,
    SetupRecommendation,
    RecommendationPackage
)


def infer_direction(
    issue,
    lever
):

    issue = issue.lower()

    #
    # Understeer
    #

    if "understeer" in issue:

        if lever == "Differential Preload":

            return (
                "decrease",
                "Higher preload generally increases entry understeer."
            )

        if lever == "Differential":

            return (
                "reduce locking",
                "More locking typically increases understeer."
            )

        if lever == "Anti-Roll Bar":

            return (
                "soften front",
                "Reducing front roll stiffness can improve rotation."
            )

        if lever == "Aero Balance":

            return (
                "shift forward",
                "Moving aero balance forward can improve turn-in."
            )

        if lever == "Ride Height":

            return (
                "increase rake",
                "More rake typically shifts aerodynamic balance forward."
            )

        if lever == "Brake Bias":

            return (
                "rearward",
                "A small rearward bias adjustment may help initial rotation."
            )

    #
    # Oversteer
    #

    if "oversteer" in issue:

        if lever == "Differential Preload":

            return (
                "increase",
                "Additional preload often improves stability."
            )

        if lever == "Differential":

            return (
                "increase locking",
                "Additional locking can stabilise the rear axle."
            )

        if lever == "Anti-Roll Bar":

            return (
                "soften rear",
                "Reducing rear roll stiffness can reduce oversteer."
            )

        if lever == "Aero Balance":

            return (
                "shift rearward",
                "Additional rear aerodynamic support can improve stability."
            )

    return (
        "investigate",
        "Further telemetry evidence is required."
    )


def build_recommendations(
    finding,
    context
):

    packet = build_knowledge(
        finding.issue,
        context=context
    )

    ranked = rank_setup_levers(
        packet
    )

    recommendations = []

    max_score = max(
        (
            item.score
            for item in ranked
        ),
        default=1
    )

    for item in ranked[:5]:

        direction, rationale = (
            infer_direction(
                finding.issue,
                item.lever
            )
        )

        confidence = (
            item.score /
            max_score
        )

        recommendations.append(

            SetupRecommendation(

                lever=item.lever,

                direction=direction,

                confidence=round(
                    confidence,
                    2
                ),

                rationale=rationale
            )
        )

    return RecommendationPackage(

        issue=finding.issue,

        vehicle=(
            context.vehicle
            if context.vehicle
            else "Unknown"
        ),

        recommendations=
            recommendations,

        telemetry_confidence=
            finding.confidence,

        setup_confidence=(
            recommendations[0].confidence
            if recommendations
            else 0.0
        )
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

    ctx = SearchContext(

        vehicle="Porsche 963 GTP",

        manufacturer="Porsche",

        car_class="GTP"
    )

    package = (
        build_recommendations(
            finding,
            ctx
        )
    )

    print("")
    print("=" * 80)
    print("Reasoned Setup Recommendations")
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

    for rec in package.recommendations:

        print(
            f"Lever: {rec.lever}"
        )

        print(
            f"Direction: {rec.direction}"
        )

        print(
            f"Confidence: {rec.confidence}"
        )

        print(
            f"Reasoning: {rec.rationale}"
        )

        print("")