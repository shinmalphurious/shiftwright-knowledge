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
            TARGET_WORDS
            - OVERLAP_WORDS
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
    print("")

    for txt_file in txt_files:

        text = txt_file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        metadata = load_metadata(
            txt_file.stem
        )

        chunks = split_into_chunks(
            text
        )

        vehicle = metadata.get(
            "vehicle",
            txt_file.stem
        )

        manufacturer = metadata.get(
            "manufacturer",
            "Unknown"
        )

        vehicle_class = metadata.get(
            "class",
            "Unknown"
        )

        topics = metadata.get(
            "topics",
            []
        )

        for local_chunk_id, chunk in enumerate(chunks):

            all_chunks.append({
                "chunk_id": chunk_id,
                "vehicle": vehicle,
                "manufacturer": manufacturer,
                "class": vehicle_class,
                "topics": topics,
                "source": txt_file.name,
                "local_chunk_id": local_chunk_id,
                "word_count": len(
                    chunk.split()
                ),
                "text": chunk
            })

            chunk_id += 1

        print(
            f"[OK] {vehicle} -> "
            f"{len(chunks)} chunks"
        )

    OUTPUT_FILE.write_text(
        json.dumps(
            all_chunks,
            indent=2
        ),
        encoding="utf-8"
    )

    print("")
    print("=" * 50)
    print("Chunk Generation Complete")
    print("=" * 50)
    print(
        f"Manuals : {len(txt_files)}"
    )
    print(
        f"Chunks  : {len(all_chunks)}"
    )
    print(
        f"Output  : {OUTPUT_FILE}"
    )
    print("")


if __name__ == "__main__":
    main()
