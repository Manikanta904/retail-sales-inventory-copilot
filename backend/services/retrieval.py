"""
Local Business Rule Retrieval Service for Retail Copilot.
Loads markdown rule documents, chunks them, and performs local vector/similarity search
using gemini-embedding-001 (or local fallback if API key is absent).
"""
import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from google import genai

from backend.core.config import DATA_DIR, GEMINI_EMBEDDING_MODEL

RULES_DIR = DATA_DIR / "rules"
CACHE_FILE = RULES_DIR / "embeddings_cache.json"
EMBEDDING_MODEL = GEMINI_EMBEDDING_MODEL



class RuleRetrievalService:
    """
    Service responsible for loading local business rules and retrieving relevant
    guidance chunks using gemini-embedding-001 and local NumPy similarity search.
    """

    def __init__(self, rules_dir: Path = RULES_DIR) -> None:
        self.rules_dir = rules_dir
        self.chunks: List[Dict[str, Any]] = []
        self.vectors: Optional[np.ndarray] = None
        self._load_and_chunk_rules()
        self._initialize_index()

    def _load_and_chunk_rules(self) -> None:
        """Reads markdown rule documents and splits them into logical section chunks."""
        self.chunks = []
        if not self.rules_dir.exists():
            return

        rule_files = list(self.rules_dir.glob("*.md"))
        chunk_counter = 1

        for filepath in rule_files:
            filename = filepath.name
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            sections = content.split("\n## ")
            for sec in sections[1:] if len(sections) > 1 else sections:
                lines = sec.strip().split("\n")
                header = lines[0].strip("# ")
                body = "\n".join(lines[1:]).strip() if len(lines) > 1 else header

                if body:
                    chunk_text = f"Document: {filename}\nSection: {header}\n{body}"
                    self.chunks.append({
                        "chunk_id": f"chunk_{chunk_counter}",
                        "source": filename,
                        "title": header,
                        "text": chunk_text,
                    })
                    chunk_counter += 1

    def _initialize_index(self) -> None:
        """Loads cached embeddings or generates them locally using gemini-embedding-001."""
        api_key = os.environ.get("GEMINI_API_KEY", "").strip()

        # 1. Check if precalculated local cache exists
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                cached_ids = [c["chunk_id"] for c in cache_data]
                current_ids = [c["chunk_id"] for c in self.chunks]

                if cached_ids == current_ids:
                    vec_list = [c["embedding"] for c in cache_data]
                    self.vectors = np.array(vec_list, dtype=np.float32)
                    self._build_vocab_map()
                    return
            except Exception:
                pass

        # 2. If API key is available, generate embeddings via SDK
        if api_key:
            try:
                client = genai.Client(api_key=api_key)
                vector_list = []
                cache_payload = []

                for chunk in self.chunks:
                    res = client.models.embed_content(
                        model=EMBEDDING_MODEL,
                        contents=chunk["text"],
                    )
                    embedding_vals = list(res.embedding.values)
                    vector_list.append(embedding_vals)
                    chunk_copy = dict(chunk)
                    chunk_copy["embedding"] = embedding_vals
                    cache_payload.append(chunk_copy)

                self.vectors = np.array(vector_list, dtype=np.float32)
                self._build_vocab_map()

                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(cache_payload, f, indent=2)
                return
            except Exception:
                pass

        # 3. Local fallback
        self._build_local_tfidf_vectors()

    def _build_vocab_map(self) -> None:
        """Builds local vocabulary map for fast offline query vectorization."""
        vocab = set()
        for c in self.chunks:
            vocab.update(c["text"].lower().split())
        vocab_list = sorted(list(vocab))
        self.vocab_map = {word: idx for idx, word in enumerate(vocab_list)}

    def _build_local_tfidf_vectors(self) -> None:
        """Fallback local keyword vectorizer when Gemini API is unreachable/offline."""
        if not self.chunks:
            self.vectors = np.zeros((0, 1), dtype=np.float32)
            return

        self._build_vocab_map()
        vocab_list = sorted(list(self.vocab_map.keys()))

        matrix = np.zeros((len(self.chunks), len(vocab_list)), dtype=np.float32)
        for i, c in enumerate(self.chunks):
            for word in c["text"].lower().split():
                if word in self.vocab_map:
                    matrix[i, self.vocab_map[word]] += 1.0

        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.vectors = matrix / norms

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top_k relevant rule chunks for a user query using cosine similarity.
        """
        if not self.chunks or self.vectors is None or len(self.vectors) == 0:
            return []

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        query_vec = None

        # Attempt API embedding if key is available
        if api_key and self.vectors.shape[1] > 200:
            try:
                client = genai.Client(api_key=api_key)
                res = client.models.embed_content(
                    model=EMBEDDING_MODEL,
                    contents=query,
                )
                query_vec = np.array(res.embedding.values, dtype=np.float32)
            except Exception:
                query_vec = None

        # Fast local vector fallback
        if query_vec is None:
            if hasattr(self, "vocab_map") and self.vectors.shape[1] == len(self.vocab_map):
                q_vec = np.zeros((len(self.vocab_map),), dtype=np.float32)
                for word in query.lower().split():
                    if word in self.vocab_map:
                        q_vec[self.vocab_map[word]] += 1.0
                norm = np.linalg.norm(q_vec)
                query_vec = q_vec / (norm if norm > 0 else 1.0)
            elif self.vectors.shape[1] == 128:
                # 128-dim cached local representation
                q_vec = np.zeros((128,), dtype=np.float32)
                if hasattr(self, "vocab_map"):
                    for word in query.lower().split():
                        if word in self.vocab_map:
                            idx = self.vocab_map[word] % 128
                            q_vec[idx] += 1.0
                norm = np.linalg.norm(q_vec)
                query_vec = q_vec / (norm if norm > 0 else 1.0)
            else:
                # Fallback keyword overlap
                scores = []
                q_words = set(query.lower().split())
                for c in self.chunks:
                    c_words = set(c["text"].lower().split())
                    scores.append(len(q_words.intersection(c_words)))
                top_indices = np.argsort(scores)[::-1][:top_k]
                return [
                    {
                        "chunk_id": self.chunks[idx]["chunk_id"],
                        "source": self.chunks[idx]["source"],
                        "title": self.chunks[idx]["title"],
                        "text": self.chunks[idx]["text"],
                        "similarity": float(scores[idx]),
                    }
                    for idx in top_indices if scores[idx] > 0
                ]

        # Compute cosine similarity
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec = query_vec / q_norm

        v_norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        v_norms[v_norms == 0] = 1.0
        norm_vectors = self.vectors / v_norms

        similarities = np.dot(norm_vectors, query_vec)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "chunk_id": self.chunks[idx]["chunk_id"],
                "source": self.chunks[idx]["source"],
                "title": self.chunks[idx]["title"],
                "text": self.chunks[idx]["text"],
                "similarity": round(float(similarities[idx]), 4),
            })

        return results
