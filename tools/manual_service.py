from pathlib import Path
import json
from dataclasses import dataclass

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

EMBEDDINGS_FILE = (
    REPO_ROOT /
    "embeddings" /
    "chunk_embeddings.npy"
)

MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

DEFAULT_TOP_K = 5


@dataclass
class SearchContext:

    vehicle: str | None = None

    manufacturer: str | None = None

    car_class: str | None = None

    track: str | None = None


class KnowledgeSearchEngine:

    def __init__(self):

        self.chunks = json.loads(
            CHUNKS_FILE.read_text(
                encoding="utf-8"
            )
        )

        self.embeddings = np.load(
            EMBEDDINGS_FILE
        )

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                MODEL_NAME
            )
        )

        self.model = (
            AutoModel.from_pretrained(
                MODEL_NAME
            )
        )

        self.model.eval()

    def mean_pooling(
        self,
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

    def embed_text(
        self,
        text
    ):

        encoded = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        with torch.no_grad():

            output = self.model(
                **encoded
            )

            embedding = (
                self.mean_pooling(
                    output,
                    encoded[
                        "attention_mask"
                    ]
                )
            )

        vector = (
            embedding
            .cpu()
            .numpy()[0]
        )

        vector /= np.linalg.norm(
            vector
        )

        return vector

    def apply_context_boosts(
        self,
        context,
        chunk,
        score
    ):

        if (
            context.vehicle
            and
            chunk["vehicle"].lower()
            ==
            context.vehicle.lower()
        ):
            score += 0.30

        if (
            context.manufacturer
            and
            chunk.get(
                "manufacturer",
                ""
            ).lower()
            ==
            context.manufacturer.lower()
        ):
            score += 0.15

        if (
            context.car_class
            and
            chunk.get(
                "class",
                ""
            ).lower()
            ==
            context.car_class.lower()
        ):
            score += 0.10

        score += (
            chunk.get(
                "section_score",
                0
            ) * 0.02
        )

        return score

    def search(
        self,
        query,
        context=None,
        top_k=DEFAULT_TOP_K
    ):

        if context is None:
            context = SearchContext()

        query_vector = (
            self.embed_text(
                query
            )
        )

        scores = np.dot(
            self.embeddings,
            query_vector
        )

        for idx, chunk in enumerate(
            self.chunks
        ):

            scores[idx] = (
                self.apply_context_boosts(
                    context,
                    chunk,
                    scores[idx]
                )
            )

        ranked = np.argsort(
            scores
        )[::-1]

        results = []

        seen_vehicles = set()

        for idx in ranked:

            chunk = self.chunks[
                int(idx)
            ]

            vehicle = chunk[
                "vehicle"
            ]

            if vehicle in seen_vehicles:
                continue

            seen_vehicles.add(
                vehicle
            )

            results.append({

                "score":
                    float(
                        scores[idx]
                    ),

                "vehicle":
                    chunk[
                        "vehicle"
                    ],

                "manufacturer":
                    chunk.get(
                        "manufacturer",
                        "Unknown"
                    ),

                "class":
                    chunk.get(
                        "class",
                        "Unknown"
                    ),

                "topics":
                    chunk.get(
                        "topics",
                        []
                    ),

                "text":
                    chunk[
                        "text"
                    ]
            })

            if (
                len(results)
                >= top_k
            ):
                break

        return results


_engine = None


def get_engine():

    global _engine

    if _engine is None:

        _engine = (
            KnowledgeSearchEngine()
        )

    return _engine


def search(
    query,
    context=None,
    top_k=5
):

    return (
        get_engine()
        .search(
            query,
            context,
            top_k
        )
    )


if __name__ == "__main__":

    ctx = SearchContext()

    results = search(
        "reduce entry understeer",
        context=ctx,
        top_k=5
    )

    for result in results:

        print("")
        print("=" * 80)

        print(
            result["vehicle"]
        )

        print(
            result["score"]
        )

        print(
            result["class"]
        )

        print("")
        print(
            result["text"][:800]
        )