from pathlib import Path
import hashlib
import json
import re

from pypdf import PdfReader


# --------------------------------------------------
# Configuration
# --------------------------------------------------

FORCE_REBUILD = True

REPO_ROOT = Path(__file__).resolve().parent.parent

PDF_DIR = REPO_ROOT / "pdf"
TEXT_DIR = REPO_ROOT / "text"
METADATA_DIR = REPO_ROOT / "metadata"

TEXT_DIR.mkdir(exist_ok=True)
METADATA_DIR.mkdir(exist_ok=True)

MANIFEST_FILE = REPO_ROOT / "text_manifest.json"


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def file_sha256(path: Path) -> str:

    h = hashlib.sha256()

    with open(path, "rb") as f:

        while True:

            chunk = f.read(65536)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def load_manifest():

    if MANIFEST_FILE.exists():

        try:
            return json.loads(
                MANIFEST_FILE.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            pass

    return {}


def save_manifest(manifest):

    MANIFEST_FILE.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True
        ),
        encoding="utf-8"
    )


# --------------------------------------------------
# Text Cleaning
# --------------------------------------------------

def clean_text(text: str) -> str:

    replacements = {
        "â€™": "'",
        "â€˜": "'",
        "â€œ": '"',
        "â€": '"',
        "â€“": "-",
        "â€”": "-",
        "Â»": "»",
        "Â«": "«",
        "Â": "",
        "\u00ad": "",
        "\ufeff": ""
    }

    for bad, good in replacements.items():
        text = text.replace(
            bad,
            good
        )

    # Attempt UTF-8 recovery for common PDF issues
    try:

        repaired = (
            text
            .encode("latin1")
            .decode(
                "utf-8",
                errors="ignore"
            )
        )

        if repaired.count("�") < text.count("�"):

            text = repaired

    except Exception:
        pass

    # Normalize whitespace
    text = re.sub(
        r"\r\n?",
        "\n",
        text
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# --------------------------------------------------
# Extraction
# --------------------------------------------------

def extract_text(pdf_path: Path):

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        try:

            page_text = page.extract_text()

            if page_text:

                pages.append(
                    f"\n\n--- PAGE {page_number} ---\n\n"
                    + page_text
                )

        except Exception as exc:

            print(
                f"Warning: page "
                f"{page_number} "
                f"failed in "
                f"{pdf_path.name}"
            )

            print(exc)

    return clean_text(
        "\n".join(pages)
    )


def process_pdf(
    pdf_file,
    manifest
):

    sha256 = file_sha256(
        pdf_file
    )

    existing = manifest.get(
        pdf_file.name
    )

    if (
        not FORCE_REBUILD
        and existing
        and existing.get("sha256")
        == sha256
    ):

        print(
            f"[SKIP] {pdf_file.name}"
        )

        return False

    print(
        f"[EXTRACT] {pdf_file.name}"
    )

    text = extract_text(
        pdf_file
    )

    txt_file = (
        TEXT_DIR /
        f"{pdf_file.stem}.txt"
    )

    txt_file.write_text(
        text,
        encoding="utf-8"
    )

    word_count = len(
        text.split()
    )

    reader = PdfReader(pdf_file)

    metadata = {
        "pdf_file": pdf_file.name,
        "text_file": txt_file.name,
        "sha256": sha256,
        "pages": len(reader.pages),
        "characters": len(text),
        "words": word_count
    }

    metadata_file = (
        METADATA_DIR /
        f"{pdf_file.stem}.json"
    )

    metadata_file.write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    manifest[pdf_file.name] = metadata

    return True


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    manifest = load_manifest()

    pdfs = sorted(
        PDF_DIR.glob("*.pdf")
    )

    print("")
    print("=" * 50)
    print(
        "iRacing Manual Text Extraction"
    )
    print("=" * 50)
    print(
        f"PDFs Found: {len(pdfs)}"
    )
    print("")

    processed = 0
    skipped = 0
    errors = 0

    for pdf_file in pdfs:

        try:

            if process_pdf(
                pdf_file,
                manifest
            ):

                processed += 1

            else:

                skipped += 1

        except Exception as exc:

            errors += 1

            print("")
            print(
                f"[ERROR] "
                f"{pdf_file.name}"
            )

            print(exc)
            print("")

    save_manifest(
        manifest
    )

    print("")
    print("=" * 50)
    print("Summary")
    print("=" * 50)
    print(
        f"Processed : {processed}"
    )
    print(
        f"Skipped   : {skipped}"
    )
    print(
        f"Errors    : {errors}"
    )
    print(
        f"Text Dir  : {TEXT_DIR}"
    )
    print("")


if __name__ == "__main__":
    main()
