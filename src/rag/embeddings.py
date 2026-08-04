"""
Embeddings generation module with caching for RAG implementation.

This module handles generation of embeddings for text chunks using sentence-transformers,
with caching to avoid regenerating embeddings for the same data.
"""

from __future__ import annotations

import hashlib
import json
import pickle
from pathlib import Path
from typing import Any

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class EmbeddingGenerator:
    """Generator for text embeddings with caching support."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: Path | None = None) -> None:
        """
        Initialize the embedding generator.

        Args:
            model_name: Name of the sentence-transformers model to use
            cache_dir: Directory for caching embeddings (defaults to data/embeddings_cache)
        """
        if SentenceTransformer is None:
            raise ImportError(
                "sentence-transformers package not installed. "
                "Run: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        
        # Set cache directory
        if cache_dir is None:
            project_root = Path(__file__).resolve().parents[2]
            cache_dir = project_root / "data" / "embeddings_cache"
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def generate_embeddings(self, chunks: list[dict[str, Any]], force_refresh: bool = False) -> list[list[float]]:
        """
        Generate embeddings for text chunks with caching.

        Args:
            chunks: List of chunk dictionaries with 'text' field
            force_refresh: Force regeneration of embeddings even if cached

        Returns:
            List of embedding vectors
        """
        # Create cache key based on chunk content
        cache_key = self._create_cache_key(chunks)
        cache_file = self.cache_dir / f"embeddings_{cache_key}.pkl"
        
        # Check if cached embeddings exist
        if not force_refresh and cache_file.exists():
            print(f"Loading cached embeddings from {cache_file}")
            with open(cache_file, "rb") as f:
                cached_data = pickle.load(f)
            
            # Verify cache matches current chunks
            if cached_data["chunk_count"] == len(chunks):
                print(f"Using cached embeddings for {len(chunks)} chunks")
                return cached_data["embeddings"]
            else:
                print("Cache mismatch, regenerating embeddings")

        # Generate new embeddings
        print(f"Generating embeddings for {len(chunks)} chunks using {self.model_name}")
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Cache the embeddings
        cache_data = {
            "embeddings": embeddings.tolist(),
            "chunk_count": len(chunks),
            "model_name": self.model_name,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }
        
        with open(cache_file, "wb") as f:
            pickle.dump(cache_data, f)
        
        print(f"Cached embeddings to {cache_file}")
        return embeddings.tolist()

    def generate_query_embedding(self, query: str) -> list[float]:
        """
        Generate embedding for a single query.

        Args:
            query: Query string

        Returns:
            Embedding vector
        """
        embedding = self.model.encode([query])
        return embedding[0].tolist()

    def _create_cache_key(self, chunks: list[dict[str, Any]]) -> str:
        """
        Create a cache key based on chunk content.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Hash string for cache key
        """
        # Create a hash based on chunk texts and IDs
        content = "".join([f"{chunk['chunk_id']}:{chunk['text'][:100]}" for chunk in chunks])
        return hashlib.md5(content.encode()).hexdigest()

    def clear_cache(self) -> None:
        """Clear all cached embeddings."""
        for cache_file in self.cache_dir.glob("embeddings_*.pkl"):
            cache_file.unlink()
            print(f"Deleted cache file: {cache_file}")

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get information about cached embeddings.

        Returns:
            Dictionary with cache information
        """
        cache_files = list(self.cache_dir.glob("embeddings_*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "cache_dir": str(self.cache_dir),
            "cache_files_count": len(cache_files),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "model_name": self.model_name
        }
