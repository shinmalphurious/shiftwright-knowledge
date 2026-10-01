from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parent.parent

TEXT_DIR = REPO_ROOT / "text"
METADATA_DIR = REPO_ROOT / "metadata"
CHUNKS_DIR = REPO_ROOT / "chunks"

CHUNKS_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = CHUNKS_DIR / "all_chunks.json"

TARGET_WORDS = 400
OVERLAP_WORDS = 100


def load_metadata(stem):

    path = METADATA_DIR / f"{stem}.json"

    if not path.exists():
        return {}

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def calculate_section_score(text):

    text = text.lower()

    score = 0

    setup_terms = [
        "setup tips",
        "anti-roll",
        "arb",
        "differential",
        "damper",
        "suspension",
        "ride height",
        "spring",
        "traction control",
        "brake bias",
        "aero balance",
        "understeer",
        "oversteer",
        "corner entry",
        "corner exit"
    ]

    low_value_terms = [
        "table of contents",
        "click to view a section",
        "dear iracing user"
    ]

    for term in setup_terms:

        if term in text:
            score += 1

    for term in low_value_terms:

        if term in text:
            score -= 5

    return score


def split_into_chunks(text):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + TARGET_WORDS

        chunk_words = words[start:end]

        chunks.append(
            " ".join(chunk_words)
        )

        start += (
            TARGET_WORDS -
            OVERLAP_WORDS
        )

    return chunks


def main():

    all_chunks = []

    chunk_id = 0

    txt_files = sorted(
        TEXT_DIR.glob("*.txt")
    )

    print("")
    print("=" * 50)
    print("Building Chunks")
    print("=" * 50)

    for txt_file in txt_files:

        text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        metadata = load_metadata(
            txt_file.stem
        )

        chunks = split_into_chunks(text)

        vehicle = metadata.get(
            "vehicle",
            txt_file.stem
        )

        for local_chunk_id, chunk in enumerate(chunks):

            all_chunks.append({

                "chunk_id": chunk_id,

                "vehicle":
                    metadata.get(
                        "vehicle",
                        txt_file.stem
                    ),

                "manufacturer":
                    metadata.get(
                        "manufacturer",
                        "Unknown"
                    ),

                "class":
                    metadata.get(
                        "class",
                        "Unknown"
                    ),

                "topics":
                    metadata.get(
                        "topics",
                        []
                    ),

                "source":
                    txt_file.name,

                "local_chunk_id":
                    local_chunk_id,

                "word_count":
                    len(chunk.split()),

                "section_score":
                    calculate_section_score(chunk),

                "text":
                    chunk
            })

            chunk_id += 1

        print(
            f"[OK] {vehicle} -> {len(chunks)}"
        )

    OUTPUT_FILE.write_text(
        json.dumps(
            all_chunks,
            indent=2
        ),
        encoding="utf-8"
    )

    print("")
    print(
        f"Chunks written: "
        f"{len(all_chunks)}"
    )


if __name__ == "__main__":
    main()
