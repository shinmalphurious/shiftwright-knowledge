from pathlib import Path
import json
import hashlib

import numpy as np
import torch

from transformers import (
    AutoTokenizer,
    AutoModel
)


REPO_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_FILE = (
    REPO_ROOT /
    "chunks" /
    "all_chunks.json"
)

EMBEDDINGS_DIR = (
    REPO_ROOT /
    "embeddings"
)

EMBEDDINGS_DIR.mkdir(
    exist_ok=True
)

EMBEDDINGS_FILE = (
    EMBEDDINGS_DIR /
    "chunk_embeddings.npy"
)

METADATA_FILE = (
    EMBEDDINGS_DIR /
    "chunk_metadata.json"
)

MANIFEST_FILE = (
    EMBEDDINGS_DIR /
    "embedding_manifest.json"
)

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

BATCH_SIZE = 32


def sha256_file(path):

    h = hashlib.sha256()

    with open(path, "rb") as f:

        while True:

            chunk = f.read(65536)

            if not chunk:
                break

            h.update(chunk)

    return h.hexdigest()


def mean_pooling(
    model_output,
    attention_mask
):

    token_embeddings = (
        model_output.last_hidden_state
    )

    mask = (
        attention_mask
        .unsqueeze(-1)
        .expand(
            token_embeddings.size()
        )
        .float()
    )

    summed = torch.sum(
        token_embeddings * mask,
        dim=1
    )

    counts = torch.clamp(
        mask.sum(dim=1),
        min=1e-9
    )

    return summed / counts


def normalize(vectors):

    norms = np.linalg.norm(
        vectors,
        axis=1,
        keepdims=True
    )

    return vectors / norms


def main():

    print("")
    print("=" * 60)
    print("Building Embeddings")
    print("=" * 60)
    print("")

    chunks_sha = sha256_file(
        CHUNKS_FILE
    )

    if MANIFEST_FILE.exists():

        manifest = json.loads(
            MANIFEST_FILE.read_text(
                encoding="utf-8"
            )
        )

        if (
            manifest.get("chunks_sha")
            == chunks_sha
        ):
            print(
                "Embeddings already current."
            )
            return

    chunks = json.loads(
        CHUNKS_FILE.read_text(
            encoding="utf-8"
        )
    )

    print(
        f"Chunks loaded: "
        f"{len(chunks)}"
    )

    texts = [
        c["text"]
        for c in chunks
    ]

    print(
        f"Loading model "
        f"{MODEL_NAME}"
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    model = AutoModel.from_pretrained(
        MODEL_NAME
    )

    model.eval()

    vectors = []

    with torch.no_grad():

        for i in range(
            0,
            len(texts),
            BATCH_SIZE
        ):

            batch = texts[
                i:i + BATCH_SIZE
            ]

            encoded = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )

            output = model(
                **encoded
            )

            embeddings = mean_pooling(
                output,
                encoded[
                    "attention_mask"
                ]
            )

            vectors.append(
                embeddings.cpu().numpy()
            )

            print(
                f"Processed "
                f"{min(i+BATCH_SIZE,len(texts))}"
                f"/{len(texts)}"
            )

    vectors = np.vstack(
        vectors
    )

    vectors = normalize(
        vectors
    )

    np.save(
        EMBEDDINGS_FILE,
        vectors
    )

    metadata = []

    for chunk in chunks:

        metadata.append({
            "chunk_id":
                chunk["chunk_id"],
            "vehicle":
                chunk["vehicle"],
            "manufacturer":
                chunk["manufacturer"],
            "class":
                chunk["class"],
            "topics":
                chunk["topics"],
            "source":
                chunk["source"]
        })

    METADATA_FILE.write_text(
        json.dumps(
            metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    MANIFEST_FILE.write_text(
        json.dumps(
            {
                "chunks_sha":
                    chunks_sha,
                "vector_count":
                    len(vectors),
                "dimensions":
                    int(
                        vectors.shape[1]
                    ),
                "model":
                    MODEL_NAME
            },
            indent=2
        ),
        encoding="utf-8"
    )

    print("")
    print("=" * 60)
    print("Embedding Build Complete")
    print("=" * 60)
    print(
        f"Vectors: {len(vectors)}"
    )
    print(
        f"Dimensions: "
        f"{vectors.shape[1]}"
    )


if __name__ == "__main__":
    main()
