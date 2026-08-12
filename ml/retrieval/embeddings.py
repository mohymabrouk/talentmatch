from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence

import numpy as np


TOKEN_PATTERN = re.compile(r"[a-z0-9][a-z0-9+#.-]*")


class HashingEmbedder:
    """Small deterministic local embedder used when a cached transformer is unavailable.

    Feature hashing gives the demo a reproducible, dependency-light cold start. The
    optional sentence-transformer implementation below can be selected for a richer
    semantic index when its model is already available locally.
    """

    name = "local-hashing-v001"

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    @staticmethod
    def _bucket(feature: str, dimension: int) -> int:
        digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        return int.from_bytes(digest, "little") % dimension

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        matrix = np.zeros((len(texts), self.dimension), dtype=np.float32)
        for row, text in enumerate(texts):
            tokens = TOKEN_PATTERN.findall(text.casefold())
            features = tokens + [f"{left}::{right}" for left, right in zip(tokens, tokens[1:])]
            for feature in features:
                bucket = self._bucket(feature, self.dimension)
                matrix[row, bucket] += 1.0
            norm = np.linalg.norm(matrix[row])
            if norm:
                matrix[row] /= norm
        return matrix


class SentenceTransformerEmbedder:
    name = "sentence-transformer"

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self.model = SentenceTransformer(model_name, local_files_only=True)
        self.dimension = int(self.model.get_sentence_embedding_dimension())

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        vectors = self.model.encode(list(texts), normalize_embeddings=True, convert_to_numpy=True)
        return np.asarray(vectors, dtype=np.float32)


def build_embedder(model_name: str, prefer_sentence_transformer: bool = True):
    if prefer_sentence_transformer:
        try:
            return SentenceTransformerEmbedder(model_name)
        except Exception:
            pass
    return HashingEmbedder()

