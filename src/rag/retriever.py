"""
Retriever module for RAG implementation.

This module handles retrieval of relevant chunks using semantic search and integrates
with the existing chatbot workflow.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.rag.chunking import ReviewChunker
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import FAISSVectorStore


class RAGRetriever:
    """Retriever for RAG implementation that integrates chunking, embeddings, and vector search."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        chunk_size: int = 400,
        cache_dir: Path | None = None,
        index_dir: Path | None = None
    ) -> None:
        """
        Initialize the RAG retriever.

        Args:
            model_name: Name of the sentence-transformers model
            chunk_size: Target chunk size in tokens
            cache_dir: Directory for embedding cache
            index_dir: Directory for vector index storage
        """
        self.chunker = ReviewChunker(target_chunk_size=chunk_size)
        self.embedding_generator = EmbeddingGenerator(model_name=model_name, cache_dir=cache_dir)
        self.vector_store = FAISSVectorStore(embedding_dim=384)  # 384 for all-MiniLM-L6-v2
        
        # Set index directory
        if index_dir is None:
            project_root = Path(__file__).resolve().parents[2]
            index_dir = project_root / "data" / "vector_index"
        
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.is_initialized = False

    def initialize_from_reviews(self, reviews: list[dict[str, Any]], force_refresh: bool = False) -> None:
        """
        Initialize the RAG system from review data.

        Args:
            reviews: List of review dictionaries
            force_refresh: Force regeneration of embeddings and index
        """
        print("Initializing RAG system from reviews...")
        
        # Step 1: Chunk the reviews
        print("Step 1: Chunking reviews...")
        chunks = self.chunker.chunk_reviews(reviews)
        chunk_stats = self.chunker.get_chunk_statistics(chunks)
        print(f"Created {chunk_stats['total_chunks']} chunks")
        print(f"Average chunk size: {chunk_stats['avg_chunk_size_tokens']:.0f} tokens")
        print(f"Average reviews per chunk: {chunk_stats['avg_reviews_per_chunk']:.1f}")
        
        # Step 2: Generate embeddings
        print("\nStep 2: Generating embeddings...")
        embeddings = self.embedding_generator.generate_embeddings(chunks, force_refresh=force_refresh)
        
        # Step 3: Create vector index
        print("\nStep 3: Creating vector index...")
        self.vector_store.create_index(embeddings, chunks)
        
        # Step 4: Save index for future use
        print("\nStep 4: Saving index...")
        index_path = self.index_dir / "reviews_index"
        self.vector_store.save_index(index_path)
        
        self.is_initialized = True
        print("\nRAG system initialization complete!")

    def load_existing_index(self) -> None:
        """Load an existing vector index from disk."""
        print("Loading existing vector index...")
        index_path = self.index_dir / "reviews_index"
        self.vector_store.load_index(index_path)
        self.is_initialized = True
        print("Vector index loaded successfully!")

    def retrieve_relevant_chunks(self, query: str, k: int = 8, min_similarity: float = 0.2) -> list[dict[str, Any]]:
        """
        Retrieve relevant chunks for a query with enhanced diversity and context.

        Args:
            query: User query string
            k: Number of chunks to retrieve (increased for better context)
            min_similarity: Minimum similarity score threshold (lowered for more results)

        Returns:
            List of relevant chunks with metadata
        """
        if not self.is_initialized:
            raise ValueError("RAG system not initialized. Call initialize_from_reviews() or load_existing_index() first.")

        # Generate query embedding
        query_embedding = self.embedding_generator.generate_query_embedding(query)
        
        # Search for similar chunks with more results initially
        initial_k = min(k * 2, 20)  # Get more results for diversity
        results = self.vector_store.search(query_embedding, k=initial_k)
        
        # Filter by minimum similarity
        filtered_results = [r for r in results if r["similarity_score"] >= min_similarity]
        
        # Add diversity by ensuring we get chunks from different parts of the dataset
        if len(filtered_results) > k:
            diverse_results = []
            seen_sources = set()
            
            for result in filtered_results:
                # Get source information if available
                chunk_id = result.get("chunk_id", "")
                source = chunk_id.split("_")[0] if "_" in chunk_id else chunk_id
                
                # If we haven't seen this source or we have few results, add it
                if source not in seen_sources or len(diverse_results) < k // 2:
                    diverse_results.append(result)
                    seen_sources.add(source)
                
                # Stop if we have enough diverse results
                if len(diverse_results) >= k:
                    break
            
            # If we didn't get enough diverse results, add the remaining ones
            if len(diverse_results) < k:
                for result in filtered_results:
                    if result not in diverse_results:
                        diverse_results.append(result)
                    if len(diverse_results) >= k:
                        break
            
            return diverse_results[:k]

        return filtered_results[:k]

    def format_retrieved_chunks(self, results: list[dict[str, Any]]) -> str:
        """
        Format retrieved chunks for inclusion in the prompt.

        Args:
            results: List of retrieval results

        Returns:
            Formatted string with chunk content
        """
        if not results:
            return "No relevant reviews found for this query."

        formatted_parts = []
        for i, result in enumerate(results, 1):
            chunk = result["chunk"]
            similarity = result["similarity_score"]
            
            formatted_parts.append(f"--- Relevant Review Chunk {i} (Similarity: {similarity:.2f}) ---")
            formatted_parts.append(chunk["text"])
            formatted_parts.append("")
        
        return "\n".join(formatted_parts)

    def get_system_status(self) -> dict[str, Any]:
        """
        Get the status of the RAG system.

        Returns:
            Dictionary with system status information
        """
        cache_info = self.embedding_generator.get_cache_info()
        index_info = self.vector_store.get_index_info()
        
        return {
            "is_initialized": self.is_initialized,
            "index_info": index_info,
            "cache_info": cache_info,
            "index_dir": str(self.index_dir)
        }

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.embedding_generator.clear_cache()
