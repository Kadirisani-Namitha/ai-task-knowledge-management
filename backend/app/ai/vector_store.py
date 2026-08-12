import logging
import os
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import faiss
import numpy as np

from app.ai.embeddings import get_embedding_dimension

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    document_id: int
    chunk_index: int
    filename: str
    text: str


class VectorStore:
    """Thin wrapper around a FAISS flat-IP index with a parallel metadata list."""

    def __init__(self, persist_dir: str) -> None:
        self._persist_dir = Path(persist_dir)
        self._index_path = self._persist_dir / "index.faiss"
        self._meta_path = self._persist_dir / "metadata.json"
        self._index: faiss.IndexFlatIP | None = None
        self._metadata: list[ChunkMetadata] = []
        self._load_or_create()

    def _load_or_create(self) -> None:
        if self._index_path.exists() and self._meta_path.exists():
            logger.info("Loading existing FAISS index from %s", self._persist_dir)
            self._index = faiss.read_index(str(self._index_path))
            with open(self._meta_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self._metadata = [ChunkMetadata(**item) for item in raw]
            logger.info("Loaded %d vectors from disk", self._index.ntotal)
        else:
            dimension = get_embedding_dimension()
            logger.info("Creating new FAISS index (dim=%d)", dimension)
            self._index = faiss.IndexFlatIP(dimension)
            self._metadata = []

    def add(self, vectors: np.ndarray, metadata_list: list[ChunkMetadata]) -> None:
        if vectors.shape[0] != len(metadata_list):
            raise ValueError("vectors and metadata must have the same length")
        self._index.add(vectors.astype(np.float32))
        self._metadata.extend(metadata_list)
        self._persist()
        logger.info("Added %d vectors (total=%d)", vectors.shape[0], self._index.ntotal)

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> list[tuple[ChunkMetadata, float]]:
        if self._index.ntotal == 0:
            return []
        top_k = min(top_k, self._index.ntotal)
        query_vector = query_vector.reshape(1, -1).astype(np.float32)
        scores, indices = self._index.search(query_vector, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self._metadata[idx], float(score)))
        return results

    def _persist(self) -> None:
        self._persist_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(self._index_path))
        with open(self._meta_path, "w", encoding="utf-8") as f:
            json.dump([asdict(m) for m in self._metadata], f, ensure_ascii=False)
        logger.info("FAISS index persisted to %s", self._persist_dir)

    @property
    def total_vectors(self) -> int:
        return self._index.ntotal if self._index else 0
