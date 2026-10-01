from pathlib import Path
import json

REPO_ROOT = Path(__file__).resolve().parent.parent

TEXT_DIR = REPO_ROOT / "text"
METADATA_DIR = REPO_ROOT / "metadata"
INDEX_DIR = REPO_ROOT / "indexes"

INDEX_DIR.mkdir(exist_ok=True)

SEARCH_INDEX = INDEX_DIR / "manual_search.json"


def load_metadata(stem):
    path = METADATA_DIR / f"{stem}.json"

    if not path.exists():
        return {}

    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def main():

    records = []

    txt_files = sorted(
        TEXT_DIR.glob("*.txt")
    )

    print(
        f"Indexing {len(txt_files)} manuals..."
    )

    for txt_file in txt_files:

        text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        metadata = load_metadata(
            txt_file.stem
        )

        records.append({
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
            "content":
                text
        })

    SEARCH_INDEX.write_text(
        json.dumps(
            records,
            indent=2
        ),
        encoding="utf-8"
    )

    print("")
    print(
        f"Created: {SEARCH_INDEX}"
    )
    print(
        f"Records: {len(records)}"
    )


if __name__ == "__main__":
    main()
