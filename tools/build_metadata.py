from pathlib import Path
import json
import re
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent

TEXT_DIR = REPO_ROOT / "text"
METADATA_DIR = REPO_ROOT / "metadata"
INDEX_DIR = REPO_ROOT / "indexes"

METADATA_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

KNOWN_VEHICLES = {

    "mustang gt3": ("Ford", "GT3"),

    "super formula lights":
        ("Toyota", "Formula"),

    "super formula sf23":
        ("Toyota", "Formula"),

    "late model stock":
        ("NASCAR", "NASCAR"),

    "streetstocks":
        ("NASCAR", "NASCAR"),

    "mini stock":
        ("NASCAR", "NASCAR"),

    "big block modified":
        ("NASCAR", "NASCAR"),

    "arca":
        ("NASCAR", "NASCAR"),

    "srx":
        ("SRX", "NASCAR"),

    "formula vee":
        ("Volkswagen", "Formula"),

    "fia f4":
        ("FIA", "Formula"),

    "shock tuning user guide":
        ("Reference", "Reference"),

    "cross car":
        ("FIA", "Rallycross"),

    "micro sprint":
        ("Sprint Car", "Dirt Oval")
}

FILENAME_MANUFACTURERS = {

    "acura": "Acura",
    "audi": "Audi",
    "aston": "Aston Martin",
    "bmw": "BMW",
    "cadillac": "Cadillac",
    "chevrolet": "Chevrolet",
    "corvette": "Chevrolet",
    "dallara": "Dallara",
    "ferrari": "Ferrari",
    "ford": "Ford",
    "mustang": "Ford",
    "honda": "Honda",
    "hyundai": "Hyundai",
    "lamborghini": "Lamborghini",
    "ligier": "Ligier",
    "mazda": "Mazda",
    "mclaren": "McLaren",
    "mercedes": "Mercedes",
    "porsche": "Porsche",
    "toyota": "Toyota"
}

MANUFACTURER_PATTERNS = {

    "Acura": ["acura", "nsx"],
    "Audi": ["audi", "r8", "rs3"],
    "Aston Martin": ["aston martin", "vantage"],
    "BMW": ["bmw"],
    "Cadillac": ["cadillac"],
    "Chevrolet": ["chevrolet", "corvette"],
    "Dallara": ["dallara"],
    "Ferrari": ["ferrari"],
    "Ford": ["ford", "mustang"],
    "Honda": ["honda"],
    "Hyundai": ["hyundai"],
    "Lamborghini": ["lamborghini"],
    "Ligier": ["ligier"],
    "Mazda": ["mazda", "mx5"],
    "McLaren": ["mclaren"],
    "Mercedes": ["mercedes", "amg"],
    "Porsche": ["porsche"],
    "Toyota": ["toyota", "gr86"]
}

TOPIC_KEYWORDS = {

    "aerodynamics": [
        "aero",
        "aerodynamic",
        "downforce",
        "rear wing"
    ],

    "tires": [
        "tire",
        "tyre",
        "pressure",
        "temperature"
    ],

    "suspension": [
        "suspension",
        "ride height",
        "spring",
        "anti-roll",
        "arb"
    ],

    "dampers": [
        "damper",
        "compression",
        "rebound"
    ],

    "differential": [
        "differential",
        "preload",
        "friction faces",
        "ramp angle"
    ],

    "brakes": [
        "brake",
        "braking",
        "bias"
    ],

    "hybrid": [
        "hybrid",
        "battery",
        "deploy"
    ],

    "traction_control": [
        "traction control"
    ]
}


def clean_vehicle_name(filename):

    vehicle = Path(filename).stem

    vehicle = re.sub(
        r"_V\d+",
        "",
        vehicle,
        flags=re.I
    )

    vehicle = re.sub(
        r"-V\d+",
        "",
        vehicle,
        flags=re.I
    )

    vehicle = re.sub(
        r"Manual",
        "",
        vehicle,
        flags=re.I
    )

    vehicle = re.sub(
        r"\bUM\b",
        "",
        vehicle,
        flags=re.I
    )

    vehicle = (
        vehicle
        .replace("_", " ")
        .replace("-", " ")
    )

    vehicle = re.sub(
        r"\s+",
        " ",
        vehicle
    )

    return vehicle.strip()


def resolve_manufacturer(
    filename,
    text
    
):
    
    if "shock" in filename.lower():

        print("")
        print("DEBUG SHOCK FILE")
        print("filename =", filename)

        normalized_filename = (
            filename.lower()
            .replace("-", " ")
            .replace("_", " ")
        )

        print(
            "normalized_filename =",
            normalized_filename
        )

        search_text = (
            filename +
            " " +
            text[:200]
        ).lower()

        print(
            "contains shock tuning user guide =",
            "shock tuning user guide" in normalized_filename
        )

        print(
            "contains shock tuning =",
            "shock tuning" in normalized_filename
        )

    filename_lower = filename.lower()

    normalized_filename = (
        filename_lower
        .replace("-", " ")
        .replace("_", " ")
    )

    #
    # Reference Documents
    #

    if "shock tuning" in normalized_filename:
        return (
            "Reference",
            "reference_override"
        )

    #
    # Series Overrides
    #

    if "nascar" in normalized_filename:
        return (
            "NASCAR",
            "series_override"
        )

    if "arca" in normalized_filename:
        return (
            "NASCAR",
            "series_override"
        )

    if "oreilly" in normalized_filename:
        return (
            "NASCAR",
            "series_override"
        )

    if "supercars" in normalized_filename:
        return (
            "Supercars",
            "series_override"
        )

    if "cross car" in normalized_filename:
        return (
            "FIA",
            "series_override"
        )

    if "micro sprint" in normalized_filename:
        return (
            "Sprint Car",
            "series_override"
        )

    #
    # Exact Filename
    #

    for key, manufacturer in (
        FILENAME_MANUFACTURERS.items()
    ):

        if key in normalized_filename:

            return (
                manufacturer,
                "filename"
            )

    #
    # Known Vehicles
    #

    search_text = (
        filename +
        " " +
        text[:5000]
    ).lower()

    search_text = (
        search_text
        .replace("-", " ")
        .replace("_", " ")
    )

    for key, data in (
        KNOWN_VEHICLES.items()
    ):

        if key in search_text:

            return (
                data[0],
                "known_vehicle"
            )

    #
    # Content Detection
    #

    scores = {}

    content = (
        filename +
        " " +
        text[:15000]
    ).lower()

    for manufacturer, patterns in (
        MANUFACTURER_PATTERNS.items()
    ):

        score = 0

        for pattern in patterns:

            score += content.count(
                pattern
            )

        if score > 0:

            scores[
                manufacturer
            ] = score

    if scores:

        return (
            max(
                scores,
                key=scores.get
            ),
            "content"
        )

    return (
        "Unknown",
        "unknown"
    )


def resolve_class(
    filename,
    text
):

    search = (
        filename +
        " " +
        text[:10000]
    ).upper()

    normalized_search = (
        search
        .replace("-", " ")
        .replace("_", " ")
    )

    #
    # Reference Documents
    #

    if "SHOCK TUNING" in normalized_search:
        return "Reference"

    #
    # Series Overrides
    #

    if "SUPERCARS" in normalized_search:
        return "Touring Car"

    if "CROSS CAR" in normalized_search:
        return "Rallycross"

    if "MICRO SPRINT" in normalized_search:
        return "Dirt Oval"

    #
    # Known Vehicles
    #

    for key, data in (
        KNOWN_VEHICLES.items()
    ):

        if key.upper() in normalized_search:
            return data[1]

    #
    # Generic Detection
    #

    if "GTP" in normalized_search:
        return "GTP"

    if "LMDH" in normalized_search:
        return "GTP"

    if "LMP2" in normalized_search:
        return "LMP2"

    if "GT3" in normalized_search:
        return "GT3"

    if "GT4" in normalized_search:
        return "GT4"

    if "TCR" in normalized_search:
        return "TCR"

    if "SUPER FORMULA" in normalized_search:
        return "Formula"

    if "FORMULA" in normalized_search:
        return "Formula"

    if "F4" in normalized_search:
        return "Formula"

    if "NASCAR" in normalized_search:
        return "NASCAR"

    if "ARCA" in normalized_search:
        return "NASCAR"

    if "DIRT" in normalized_search:
        return "Dirt Oval"

    return "Unknown"


def detect_topics(text):

    lower = text.lower()

    topics = []

    for topic, keywords in TOPIC_KEYWORDS.items():

        if any(
            keyword in lower
            for keyword in keywords
        ):
            topics.append(topic)

    return sorted(topics)


def detect_sections(text):

    candidates = [

        "Tires & Aero",
        "Setup Tips",
        "Chassis",
        "Dampers",
        "Differential",
        "Brakes",
        "Hybrid",
        "Fuel",
        "Traction Control"
    ]

    lower = text.lower()

    found = []

    for candidate in candidates:

        if candidate.lower() in lower:
            found.append(candidate)

    return found


def determine_manual_type(
    manufacturer,
    vehicle_class
):

    if (
        manufacturer == "Reference"
        or
        vehicle_class == "Reference"
    ):
        return "reference"

    return "vehicle"


def main():

    manufacturer_index = defaultdict(list)
    class_index = defaultdict(list)
    topic_index = defaultdict(list)

    txt_files = sorted(
        TEXT_DIR.glob("*.txt")
    )

    print("")
    print("=" * 60)
    print("Building Metadata")
    print("=" * 60)

    for txt_file in txt_files:

        text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        vehicle = clean_vehicle_name(
            txt_file.name
        )

        manufacturer, source = (
            resolve_manufacturer(
                txt_file.name,
                text
            )
        )

        vehicle_class = (
            resolve_class(
                txt_file.name,
                text
            )
        )

        metadata = {

            "vehicle":
                vehicle,

            "manufacturer":
                manufacturer,

            "manufacturer_source":
                source,

            "class":
                vehicle_class,

            "manual_type":
                determine_manual_type(
                    manufacturer,
                    vehicle_class
                ),

            "topics":
                detect_topics(text),

            "sections":
                detect_sections(text),

            "word_count":
                len(text.split()),

            "source_text":
                txt_file.name
        }

        (
            METADATA_DIR /
            f"{txt_file.stem}.json"
        ).write_text(

            json.dumps(
                metadata,
                indent=2
            ),

            encoding="utf-8"
        )

        manufacturer_index[
            manufacturer
        ].append(vehicle)

        class_index[
            vehicle_class
        ].append(vehicle)

        for topic in metadata["topics"]:

            topic_index[
                topic
            ].append(vehicle)

        print(
            f"[OK] {vehicle} -> {manufacturer}"
        )

    (
        INDEX_DIR /
        "manufacturers.json"
    ).write_text(

        json.dumps(
            dict(manufacturer_index),
            indent=2,
            sort_keys=True
        ),

        encoding="utf-8"
    )

    (
        INDEX_DIR /
        "classes.json"
    ).write_text(

        json.dumps(
            dict(class_index),
            indent=2,
            sort_keys=True
        ),

        encoding="utf-8"
    )

    (
        INDEX_DIR /
        "topics.json"
    ).write_text(

        json.dumps(
            dict(topic_index),
            indent=2,
            sort_keys=True
        ),

        encoding="utf-8"
    )

    print("")
    print("=" * 60)
    print("Metadata Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()