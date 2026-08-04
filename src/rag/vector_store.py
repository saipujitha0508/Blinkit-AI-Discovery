"""
Vector store module using FAISS for RAG implementation.

This module handles storage and retrieval of embeddings using FAISS for efficient
similarity search.
"""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

try:
    import faiss
except ImportError:
    faiss = None

import numpy as np


class FAISSVectorStore:
    """Vector store using FAISS for efficient similarity search."""

    def __init__(self, embedding_dim: int = 384, index_type: str = "flat") -> None:
        """
        Initialize the FAISS vector store.

        Args:
            embedding_dim: Dimension of embedding vectors (default: 384 for all-MiniLM-L6-v2)
            index_type: Type of FAISS index ('flat' for exact search, 'ivf' for approximate)
        """
        if faiss is None:
            raise ImportError(
                "faiss package not installed. "
                "Run: pip install faiss-cpu"
            )

        self.embedding_dim = embedding_dim
        self.index_type = index_type
        self.index = None
        self.chunks = []  # Store chunk metadata alongside the index

    def create_index(self, embeddings: list[list[float]], chunks: list[dict[str, Any]]) -> None:
        """
        Create FAISS index from embeddings.

        Args:
            embeddings: List of embedding vectors
            chunks: List of chunk dictionaries with metadata
        """
        # Convert embeddings to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Create appropriate index type
        if self.index_type == "flat":
            # Flat index for exact search
            self.index = faiss.IndexFlat(self.embedding_dim)
        elif self.index_type == "ivf":
            # IVF index for approximate search (faster for large datasets)
            quantizer = faiss.IndexFlat(self.embedding_dim)
            nlist = min(100, len(embeddings) // 10)  # Number of clusters
            self.index = faiss.IndexIVFFlat(quantizer, self.embedding_dim, nlist)
            self.index.train(embeddings_array)
        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

        # Add embeddings to index
        self.index.add(embeddings_array)
        
        # Store chunk metadata
        self.chunks = chunks
        
        print(f"Created FAISS {self.index_type} index with {self.index.ntotal} vectors")

    def search(self, query_embedding: list[float], k: int = 5) -> list[dict[str, Any]]:
        """
        Search for similar chunks using query embedding.

        Args:
            query_embedding: Embedding vector for the query
            k: Number of results to return

        Returns:
            List of dictionaries with chunk metadata and similarity scores
        """
        if self.index is None:
            raise ValueError("Index not created. Call create_index() first.")

        # Convert query to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search the index
        distances, indices = self.index.search(query_array, k)
        
        # Format results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < len(self.chunks):  # Ensure valid index
                result = {
                    "chunk": self.chunks[idx],
                    "similarity_score": float(1 / (1 + distance)),  # Convert distance to similarity
                    "distance": float(distance),
                    "rank": i + 1
                }
                results.append(result)
        
        return results

    def save_index(self, save_path: Path) -> None:
        """
        Save the FAISS index and chunk metadata to disk.

        Args:
            save_path: Path to save the index (without extension)
        """
        if self.index is None:
            raise ValueError("Index not created. Call create_index() first.")

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = save_path.with_suffix(".index")
        faiss.write_index(self.index, str(index_file))
        
        # Save chunk metadata
        metadata_file = save_path.with_suffix(".pkl")
        with open(metadata_file, "wb") as f:
            pickle.dump(self.chunks, f)
        
        print(f"Saved index to {index_file} and metadata to {metadata_file}")

    def load_index(self, load_path: Path) -> None:
        """
        Load FAISS index and chunk metadata from disk.

        Args:
            load_path: Path to load the index from (without extension)
        """
        load_path = Path(load_path)
        
        # Load FAISS index
        index_file = load_path.with_suffix(".index")
        if not index_file.exists():
            raise FileNotFoundError(f"Index file not found: {index_file}")
        
        self.index = faiss.read_index(str(index_file))
        
        # Load chunk metadata
        metadata_file = load_path.with_suffix(".pkl")
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")
        
        with open(metadata_file, "rb") as f:
            self.chunks = pickle.load(f)
        
        print(f"Loaded index from {index_file} with {self.index.ntotal} vectors")

    def get_index_info(self) -> dict[str, Any]:
        """
        Get information about the current index.

        Returns:
            Dictionary with index information
        """
        if self.index is None:
            return {
                "status": "not_created",
                "index_type": self.index_type,
                "embedding_dim": self.embedding_dim
            }

        return {
            "status": "created",
            "index_type": self.index_type,
            "embedding_dim": self.embedding_dim,
            "total_vectors": self.index.ntotal,
            "total_chunks": len(self.chunks),
            "is_trained": hasattr(self.index, 'is_trained') and self.index.is_trained
        }
