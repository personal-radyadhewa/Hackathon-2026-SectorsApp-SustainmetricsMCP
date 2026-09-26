"""Embedded Vector Store for OJK TKBI 2024 Sustainable Finance Taxonomy.

Zero-C++ native implementation using SQLite and NumPy cosine similarity.
Supports offline deterministic embeddings with optional OpenAI API upgrade.
"""

import hashlib
import json
import logging
import math
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Optional

import numpy as np

logger = logging.getLogger("sustainmetric.tkbi_vector_store")

DB_PATH_DEFAULT = Path(".cache/tkbi_vectors.db")
SEEDS_FILE = Path(__file__).parent / "data" / "tkbi_2024_seeds.json"
VECTOR_DIM = 384


def _deterministic_offline_embed(text: str, dim: int = VECTOR_DIM) -> np.ndarray:
    """Generate deterministic normalized L2 vector using token feature hashing and n-grams."""
    vec = np.zeros(dim, dtype=np.float32)
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [t for t in cleaned.split() if len(t) > 1]
    
    # 1-grams and 2-grams
    ngrams = tokens.copy()
    for i in range(len(tokens) - 1):
        ngrams.append(f"{tokens[i]}_{tokens[i+1]}")

    for token in ngrams:
        # 3 independent hash projections for collision reduction
        h1 = int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16) % dim
        h2 = int(hashlib.sha1(token.encode("utf-8")).hexdigest()[:8], 16) % dim
        h3 = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) % dim
        vec[h1] += 1.0
        vec[h2] += 0.5
        vec[h3] += 0.25

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


class TKBIVectorStore:
    """Persistent SQLite-backed vector store with cosine similarity retrieval."""

    def __init__(self, db_path: Optional[Path] = None, openai_api_key: Optional[str] = None):
        self.db_path = db_path or DB_PATH_DEFAULT
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self._init_db()
        self.seed_defaults_if_empty()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tkbi_documents (
                    id TEXT PRIMARY KEY,
                    sector TEXT NOT NULL,
                    subsector TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    criteria_level TEXT NOT NULL,
                    tsc TEXT NOT NULL,
                    dnsh TEXT NOT NULL,
                    mss TEXT NOT NULL,
                    full_text TEXT NOT NULL,
                    embedding BLOB NOT NULL
                )
                """
            )
            conn.commit()
        finally:
            conn.close()

    def get_embedding(self, text: str) -> np.ndarray:
        """Fetch embedding from OpenAI API if key exists, else use offline deterministic vector."""
        if self.openai_api_key:
            try:
                import httpx
                resp = httpx.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"input": text, "model": "text-embedding-3-small", "dimensions": VECTOR_DIM},
                    timeout=5.0,
                )
                if resp.status_code == 200:
                    raw_emb = resp.json()["data"][0]["embedding"]
                    arr = np.array(raw_emb, dtype=np.float32)
                    norm = np.linalg.norm(arr)
                    return arr / norm if norm > 0 else arr
            except Exception as e:
                logger.warning(f"OpenAI embedding call failed, falling back to offline: {e}")

        return _deterministic_offline_embed(text, VECTOR_DIM)

    def upsert_document(self, doc: dict[str, Any]) -> None:
        """Insert or update a TKBI taxonomy rule document."""
        doc_id = doc["id"]
        keywords_str = " ".join(doc.get("keywords", []))
        full_text = f"{doc['sector']} {doc['subsector']} {doc['activity']} {doc['criteria_level']} {doc['tsc']} {doc['dnsh']} {doc['mss']} {keywords_str}"
        embedding = self.get_embedding(full_text)
        blob = embedding.tobytes()

        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO tkbi_documents
                (id, sector, subsector, activity, criteria_level, tsc, dnsh, mss, full_text, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc_id,
                    doc["sector"],
                    doc["subsector"],
                    doc["activity"],
                    doc["criteria_level"],
                    doc["tsc"],
                    doc["dnsh"],
                    doc["mss"],
                    full_text,
                    blob,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def seed_defaults_if_empty(self) -> None:
        """Seed pre-defined OJK TKBI 2024 documents if store is uninitialized."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) FROM tkbi_documents")
            count = cursor.fetchone()[0]
        finally:
            conn.close()

        if count > 0:
            return

        if SEEDS_FILE.exists():
            with open(SEEDS_FILE, "r", encoding="utf-8") as f:
                seeds = json.load(f)
            for doc in seeds:
                self.upsert_document(doc)
            logger.info(f"Seeded {len(seeds)} TKBI 2024 taxonomy documents.")

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """Semantic search returning top-k matching TKBI taxonomy clauses with similarity score."""
        query_emb = self.get_embedding(query)
        results = []

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, sector, subsector, activity, criteria_level, tsc, dnsh, mss, embedding FROM tkbi_documents"
            )
            rows = cursor.fetchall()
        finally:
            conn.close()

        for doc_id, sector, subsector, activity, criteria_level, tsc, dnsh, mss, blob in rows:
            doc_emb = np.frombuffer(blob, dtype=np.float32)
            sim = float(np.dot(query_emb, doc_emb))
            results.append({
                "id": doc_id,
                "sector": sector,
                "subsector": subsector,
                "activity": activity,
                "criteria_level": criteria_level,
                "tsc": tsc,
                "dnsh": dnsh,
                "mss": mss,
                "similarity_score": round(max(0.0, min(1.0, (sim + 1.0) / 2.0)), 4),
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def get_document_by_id(self, doc_id: str) -> Optional[dict[str, Any]]:
        """Retrieve single TKBI criteria document by ID."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT id, sector, subsector, activity, criteria_level, tsc, dnsh, mss FROM tkbi_documents WHERE id = ?",
                (doc_id,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if not row:
            return None
        return {
            "id": row[0],
            "sector": row[1],
            "subsector": row[2],
            "activity": row[3],
            "criteria_level": row[4],
            "tsc": row[5],
            "dnsh": row[6],
            "mss": row[7],
        }
