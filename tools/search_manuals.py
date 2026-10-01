from pathlib import Path
import json
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent

INDEX_FILE = (
    REPO_ROOT /
    "indexes" /
    "manual_search.json"
)


def snippet(
    text,
    keyword,
    radius=250
):

    pos = text.lower().find(
        keyword.lower()
    )

    if pos < 0:
        return ""

    start = max(
        pos - radius,
        0
    )

    end = min(
        pos + radius,
        len(text)
    )

    return text[start:end]


def main():

    if len(sys.argv) < 2:

        print(
            "Usage:"
        )

        print(
            "python tools\\search_manuals.py keyword"
        )

        return

    query = " ".join(
        sys.argv[1:]
    )

    index = json.loads(
        INDEX_FILE.read_text(
            encoding="utf-8"
        )
    )

    matches = []

    for record in index:

        text = record[
            "content"
        ]

        count = text.lower().count(
            query.lower()
        )

        if count > 0:

            matches.append(
                (
                    count,
                    record
                )
            )

    matches.sort(
        reverse=True,
        key=lambda x: x[0]
    )

    print("")
    print(
        f"Search: {query}"
    )

    print(
        f"Matches: {len(matches)}"
    )

    print("")

    for count, record in matches[:20]:

        print("=" * 80)

        print(
            f"Vehicle: "
            f"{record['vehicle']}"
        )

        print(
            f"Class: "
            f"{record['class']}"
        )

        print(
            f"Hits: "
            f"{count}"
        )

        print("")

        print(
            snippet(
                record["content"],
                query
            )
        )

        print("")
        print("")

if __name__ == "__main__":
    main()
