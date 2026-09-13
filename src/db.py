"""
GeoPulse 
Changes from v1:
  • max_results bumped to 3 (richer multi-precedent context)
  • query returns distance scores so agents can weight by similarity
  • get_collection_stats() helper for UI health check
  • category-based pre-filter support via ChromaDB where-clause
"""

import os
import json
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()


class GeopoliticalVectorStore:
    def __init__(self):
        self.db_path = os.getenv("CHROMA_DB_PATH", "./vector_store")

        self.client = chromadb.PersistentClient(path=self.db_path)

        # Upgraded: all-mpnet-base-v2 is larger and semantically richer
        # than all-MiniLM-L6-v2 at marginal cost for offline inference.
        # Falls back to MiniLM if mpnet not available.
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=model_name
        )

        self.collection = self.client.get_or_create_collection(
            name="geopolitical_knowledge_base",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    # ─────────────────────────────────────────────
    # Seeding
    # ─────────────────────────────────────────────

    def seed_database_from_json(self, json_file_path: str) -> int:
        """
        Reads raw_history.json and upserts into ChromaDB.
        Returns count of records indexed.
        """
        path = Path(json_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Data source not found: {json_file_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"🔄 Indexing {len(data)} historical crisis profiles...")

        for item in data:
            metadata = {
                "event_name":        item["event"],
                "category":          item["metadata"]["category"],
                "primary_commodity": item["metadata"]["primary_commodity"],
                "macro_regime":      item["metadata"]["macro_regime"],
            }
            # Store year if present
            if "year" in item.get("metadata", {}):
                metadata["year"] = str(item["metadata"]["year"])

            self.collection.upsert(
                ids=[item["crisis_id"]],
                documents=[item["context"]],
                metadatas=[metadata]
            )

        print(f"✅ {len(data)} profiles indexed.")
        return len(data)

    # ─────────────────────────────────────────────
    # Retrieval
    # ─────────────────────────────────────────────

    def query_historical_context(
        self,
        current_headline: str,
        max_results: int = 3,
        category_filter: str | None = None,
    ) -> list[dict]:
        """
        Semantic similarity search against the archive.

        Returns list of dicts:
            text, associated_event, regime_impact, similarity_score,
            category, primary_commodity, year (if present)

        max_results=3 by default – richer multi-precedent context.
        category_filter: optional ChromaDB where-clause on 'category' field.
        """
        query_kwargs: dict = {
            "query_texts": [current_headline],
            "n_results":   min(max_results, self.collection.count() or 1),
            "include":     ["documents", "metadatas", "distances"],
        }
        if category_filter:
            query_kwargs["where"] = {"category": {"$eq": category_filter}}

        results = self.collection.query(**query_kwargs)

        extracted = []
        if results and results["documents"] and results["documents"][0]:
            docs      = results["documents"][0]
            metas     = results["metadatas"][0]
            distances = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance → similarity score (0-100)
                similarity = round((1 - dist) * 100, 1)
                extracted.append({
                    "text":              doc,
                    "associated_event":  meta.get("event_name", "Unknown"),
                    "regime_impact":     meta.get("macro_regime", "Unknown"),
                    "category":          meta.get("category", "General"),
                    "primary_commodity": meta.get("primary_commodity", ""),
                    "year":              meta.get("year", ""),
                    "similarity_score":  similarity,
                })

        # Sort by descending similarity
        extracted.sort(key=lambda x: x["similarity_score"], reverse=True)
        return extracted

    # ─────────────────────────────────────────────
    # Utilities
    # ─────────────────────────────────────────────

    def get_collection_stats(self) -> dict:
        """Returns basic stats for UI health panel."""
        count = self.collection.count()
        return {
            "total_profiles": count,
            "db_path":        self.db_path,
            "collection":     "geopolitical_knowledge_base",
        }

    def is_seeded(self) -> bool:
        return self.collection.count() > 0
