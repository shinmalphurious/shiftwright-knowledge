from dataclasses import dataclass
import re

from manual_service import (
    search,
    SearchContext
)


from engineering_models import (
KnowledgePacket
)


def extract_setup_levers(text):

    text_lower = text.lower()

    lever_map = {

        "Anti-Roll Bar": [
            "arb",
            "anti-roll"
        ],

        "Differential": [
            "differential"
        ],

        "Differential Preload": [
            "preload"
        ],

        "Aero Balance": [
            "aero balance",
            "rear wing",
            "rake"
        ],

        "Ride Height": [
            "ride height"
        ],

        "Brake Bias": [
            "brake bias"
        ],

        "Traction Control": [
            "traction control"
        ]
    }

    levers = []

    for lever, terms in (
        lever_map.items()
    ):

        if any(
            term in text_lower
            for term in terms
        ):
            levers.append(
                lever
            )

    return sorted(
        set(levers)
    )


def extract_effects(text):

    effects = []

    patterns = [

        r"(Increasing .*?understeer)",

        r"(Increasing .*?oversteer)",

        r"(Reducing .*?understeer)",

        r"(Reducing .*?oversteer)",

        r"(More .*?understeer)",

        r"(More .*?oversteer)",

        r"(Less .*?understeer)",

        r"(Less .*?oversteer)"
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            match = re.sub(
                r"--- PAGE.*",
                "",
                match
            )

            match = re.sub(
                r"\s+",
                " ",
                match
            )

            match = match.strip()

            if len(match) > 20:

                effects.append(
                    match
                )

    return sorted(
        set(effects)
    )


def build_knowledge(
    query,
    context=None,
    top_k=5
):

    if context is None:

        context = SearchContext()

    results = search(
        query,
        context=context,
        top_k=top_k
    )

    setup_levers = set()

    setup_effects = []

    evidence = []

    for result in results:

        text = result["text"]

        for lever in extract_setup_levers(
            text
        ):

            setup_levers.add(
                lever
            )

        setup_effects.extend(
            extract_effects(
                text
            )
        )

        evidence.append({

            "vehicle":
                result[
                    "vehicle"
                ],

            "score":
                result[
                    "score"
                ],

            "excerpt":
                text[:600]
        })

    return KnowledgePacket(

        query=query,

        vehicle=context.vehicle,

        manufacturer=context.manufacturer,

        car_class=context.car_class,

        setup_levers=sorted(
            setup_levers
        ),

        setup_effects=sorted(
            set(
                setup_effects
            )
        ),

        evidence=evidence,

        raw_results=results
    )


if __name__ == "__main__":

    ctx = SearchContext(

        vehicle="Porsche 963 GTP",

        manufacturer="Porsche",

        car_class="GTP"
    )

    packet = build_knowledge(

        "entry understeer",

        context=ctx
    )

    print("")
    print("=" * 80)
    print("Knowledge Packet")
    print("=" * 80)

    print("")
    print("Setup Levers:")

    for lever in packet.setup_levers:

        print(
            f" - {lever}"
        )

    print("")
    print("Effects:")

    for effect in packet.setup_effects[:15]:

        print(
            f" - {effect}"
        )

    print("")
    print("Evidence:")

    for item in packet.evidence[:3]:

        print("")

        print(
            item["vehicle"]
        )

        print(
            item["score"]
        )