from engineering_models import (
    RankedLever
)


ISSUE_RULES = {

    "entry_understeer": {

        "Differential Preload": [
            "preload",
            "locking",
            "understeer"
        ],

        "Differential": [
            "differential",
            "locking",
            "understeer"
        ],

        "Anti-Roll Bar": [
            "arb",
            "anti-roll",
            "understeer"
        ],

        "Aero Balance": [
            "aero balance",
            "rake",
            "rear wing"
        ],

        "Brake Bias": [
            "brake bias",
            "turn-in",
            "rotation"
        ]
    },

    "mid_corner_understeer": {

        "Anti-Roll Bar": [
            "arb",
            "anti-roll",
            "understeer"
        ],

        "Ride Height": [
            "ride height",
            "rake"
        ],

        "Aero Balance": [
            "aero balance",
            "rear wing"
        ]
    },

    "exit_understeer": {

        "Differential": [
            "differential"
        ],

        "Differential Preload": [
            "preload"
        ],

        "Traction Control": [
            "traction control",
            "traction"
        ]
    },

    "entry_oversteer": {

        "Differential Preload": [
            "preload",
            "oversteer"
        ],

        "Differential": [
            "differential",
            "oversteer"
        ],

        "Anti-Roll Bar": [
            "arb",
            "oversteer"
        ]
    },

    "poor_rotation": {

        "Differential": [
            "rotation",
            "differential"
        ],

        "Anti-Roll Bar": [
            "rotation",
            "arb"
        ],

        "Brake Bias": [
            "brake bias",
            "rotation"
        ],

        "Aero Balance": [
            "aero balance",
            "rotation"
        ]
    }
}


def normalize_issue(
    issue
):

    issue = issue.lower()

    if (
        "entry" in issue
        and
        "understeer" in issue
    ):
        return "entry_understeer"

    if (
        "mid" in issue
        and
        "understeer" in issue
    ):
        return "mid_corner_understeer"

    if (
        "exit" in issue
        and
        "understeer" in issue
    ):
        return "exit_understeer"

    if (
        "entry" in issue
        and
        "oversteer" in issue
    ):
        return "entry_oversteer"

    if "rotation" in issue:
        return "poor_rotation"

    return "entry_understeer"


def rank_setup_levers(
    packet
):

    issue_type = normalize_issue(
        packet.query
    )

    rules = ISSUE_RULES[
        issue_type
    ]

    ranked = []

    for lever in (
        packet.setup_levers
    ):

        keywords = rules.get(
            lever,
            []
        )

        score = 0

        evidence_count = 0

        reasons = []

        for evidence in (
            packet.evidence
        ):

            text = (
                evidence[
                    "excerpt"
                ]
                .lower()
            )

            local_score = 0

            for keyword in (
                keywords
            ):

                if keyword in text:

                    local_score += 1

            if local_score:

                score += (
                    local_score
                )

                evidence_count += 1

                reasons.append(
                    evidence[
                        "vehicle"
                    ]
                )

        ranked.append(

            RankedLever(

                lever=lever,

                score=float(score),

                evidence_count=
                    evidence_count,

                reasons=
                    sorted(
                        set(
                            reasons
                        )
                    )
            )
        )

    ranked.sort(

        key=lambda x:
            x.score,

        reverse=True
    )

    return ranked
