from pathlib import Path
import json
import numpy as np
import torch

from transformers import (
    AutoTokenizer,
    AutoModel
)

REPO_ROOT = Path(__file__).resolve().parent.parent

EMBEDDINGS_FILE = (
    REPO_ROOT /
    "embeddings" /
    "chunk_embeddings.npy"
)

CHUNKS_FILE = (
    REPO_ROOT /
    "chunks" /
    "all_chunks.json"
)

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K = 10

MAX_CHUNKS_PER_VEHICLE = 1
MAX_CHUNKS_PER_MANUFACTURER = 2


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


def embed_query(
    query,
    tokenizer,
    model
):

    encoded = tokenizer(
        query,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    with torch.no_grad():

        output = model(
            **encoded
        )

        embedding = mean_pooling(
            output,
            encoded[
                "attention_mask"
            ]
        )

    vector = (
        embedding
        .cpu()
        .numpy()[0]
    )

    norm = np.linalg.norm(
        vector
    )

    return vector / norm


def rerank_scores(
    query,
    chunks,
    semantic_scores
):

    scores = semantic_scores.copy()

    query_lower = query.lower()

    low_value_phrases = [

        "table of contents",
        "click to view a section",
        "dear iracing user",
        "general information",
        "introduction"
    ]

    for idx, chunk in enumerate(chunks):

        text = chunk[
            "text"
        ].lower()

        #
        # Section quality bonus
        #

        scores[idx] += (
            chunk.get(
                "section_score",
                0
            ) * 0.02
        )

        #
        # Penalise low value chunks
        #

        for phrase in low_value_phrases:

            if phrase in text:

                scores[idx] -= 0.25

        #
        # Understeer
        #

        if "understeer" in query_lower:

            if "understeer" in text:
                scores[idx] += 0.10

            if "anti-roll" in text:
                scores[idx] += 0.08

            if "arb" in text:
                scores[idx] += 0.08

            if "corner entry" in text:
                scores[idx] += 0.08

            if "differential" in text:
                scores[idx] += 0.05

        #
        # Oversteer
        #

        if "oversteer" in query_lower:

            if "oversteer" in text:
                scores[idx] += 0.10

            if "anti-roll" in text:
                scores[idx] += 0.08

            if "arb" in text:
                scores[idx] += 0.08

            if "differential" in text:
                scores[idx] += 0.05

        #
        # Traction
        #

        if "traction" in query_lower:

            if "corner exit" in text:
                scores[idx] += 0.12

            if "traction control" in text:
                scores[idx] += 0.10

            if "differential" in text:
                scores[idx] += 0.08

            if "rear tyre" in text:
                scores[idx] += 0.05

            if "rear tire" in text:
                scores[idx] += 0.05

        #
        # Aero
        #

        if (
            "aero" in query_lower
            or
            "downforce" in query_lower
        ):

            if "aero balance" in text:
                scores[idx] += 0.12

            if "downforce" in text:
                scores[idx] += 0.10

            if "rear wing" in text:
                scores[idx] += 0.08

            if "ride height" in text:
                scores[idx] += 0.08

        #
        # Hybrid
        #

        if "hybrid" in query_lower:

            if "hybrid" in text:
                scores[idx] += 0.15

            if "deploy" in text:
                scores[idx] += 0.10

            if "battery" in text:
                scores[idx] += 0.08

        #
        # Dampers
        #

        if "damper" in query_lower:

            if "damper" in text:
                scores[idx] += 0.15

            if "compression" in text:
                scores[idx] += 0.08

            if "rebound" in text:
                scores[idx] += 0.08

        #
        # Differential
        #

        if "differential" in query_lower:

            if "differential" in text:
                scores[idx] += 0.15

            if "preload" in text:
                scores[idx] += 0.10

            if "friction faces" in text:
                scores[idx] += 0.08

            if "ramp angle" in text:
                scores[idx] += 0.08

    return scores


def build_diverse_results(
    scores,
    chunks
):

    ranked = np.argsort(
        scores
    )[::-1]

    best = []

    vehicle_counts = {}
    manufacturer_counts = {}

    for idx in ranked:

        chunk = chunks[
            int(idx)
        ]

        vehicle = chunk[
            "vehicle"
        ]

        manufacturer = chunk.get(
            "manufacturer",
            "Unknown"
        )

        if (
            vehicle_counts.get(
                vehicle,
                0
            )
            >= MAX_CHUNKS_PER_VEHICLE
        ):
            continue

        if (
            manufacturer_counts.get(
                manufacturer,
                0
            )
            >= MAX_CHUNKS_PER_MANUFACTURER
        ):
            continue

        best.append(
            int(idx)
        )

        vehicle_counts[
            vehicle
        ] = (
            vehicle_counts.get(
                vehicle,
                0
            ) + 1
        )

        manufacturer_counts[
            manufacturer
        ] = (
            manufacturer_counts.get(
                manufacturer,
                0
            ) + 1
        )

        if len(best) >= TOP_K:
            break

    return best


def main():

    import sys

    if len(sys.argv) < 2:

        print("")
        print(
            "Usage:"
        )

        print(
            "python tools\\search_semantic.py query"
        )

        print("")

        return

    query = " ".join(
        sys.argv[1:]
    )

    print("")
    print(
        f'Semantic Search: "{query}"'
    )

    print("")

    embeddings = np.load(
        EMBEDDINGS_FILE
    )

    chunks = json.loads(
        CHUNKS_FILE.read_text(
            encoding="utf-8"
        )
    )

    print(
        "Loading model..."
    )

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME
    )

    model = AutoModel.from_pretrained(
        MODEL_NAME
    )

    query_vector = embed_query(
        query,
        tokenizer,
        model
    )

    semantic_scores = np.dot(
        embeddings,
        query_vector
    )

    scores = rerank_scores(
        query,
        chunks,
        semantic_scores
    )

    best = build_diverse_results(
        scores,
        chunks
    )

    print("")
    print(
        "Top Results"
    )

    print("=" * 80)

    for rank, idx in enumerate(
        best,
        start=1
    ):

        chunk = chunks[idx]

        print("")
        print(
            f"Rank: {rank}"
        )

        print(
            f"Score: "
            f"{scores[idx]:.4f}"
        )

        print(
            f"Vehicle: "
            f"{chunk['vehicle']}"
        )

        print(
            f"Manufacturer: "
            f"{chunk.get('manufacturer','Unknown')}"
        )

        print(
            f"Class: "
            f"{chunk['class']}"
        )

        print(
            f"Source: "
            f"{chunk['source']}"
        )

        print(
            f"Chunk: "
            f"{chunk['local_chunk_id']}"
        )

        print("")

        preview = (
            chunk["text"][:1200]
            .replace(
                "\n",
                " "
            )
        )

        print(preview)

        print("")
        print(
            "-" * 80
        )

    print("")


if __name__ == "__main__":
    main()