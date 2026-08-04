"""
Test script for RAG implementation.

This script tests the RAG components to ensure they work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.local_store import load_json
from src.rag.chunking import ReviewChunker
from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import FAISSVectorStore
from src.rag.retriever import RAGRetriever


def test_chunking():
    """Test the chunking functionality."""
    print("=== Testing Chunking ===")
    
    # Load sample reviews
    reviews_file = PROJECT_ROOT / "data" / "store" / "reviews_sampled_3000.json"
    reviews = load_json(reviews_file).get("reviews", [])
    
    print(f"Loaded {len(reviews)} reviews")
    
    # Test chunking
    chunker = ReviewChunker(target_chunk_size=400)
    chunks = chunker.chunk_reviews(reviews)
    
    stats = chunker.get_chunk_statistics(chunks)
    print(f"Created {stats['total_chunks']} chunks")
    print(f"Average chunk size: {stats['avg_chunk_size_tokens']:.0f} tokens")
    print(f"Average reviews per chunk: {stats['avg_reviews_per_chunk']:.1f}")
    print(f"Min chunk size: {stats['min_chunk_size']} tokens")
    print(f"Max chunk size: {stats['max_chunk_size']} tokens")
    
    return chunks


def test_embeddings(chunks):
    """Test the embedding generation."""
    print("\n=== Testing Embeddings ===")
    
    # Test embedding generation
    generator = EmbeddingGenerator()
    
    # Test with a small subset first
    test_chunks = chunks[:10]
    print(f"Testing with {len(test_chunks)} chunks")
    
    embeddings = generator.generate_embeddings(test_chunks, force_refresh=True)
    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimension: {len(embeddings[0])}")
    
    # Test query embedding
    query = "What do customers think about delivery speed?"
    query_embedding = generator.generate_query_embedding(query)
    print(f"Query embedding dimension: {len(query_embedding)}")
    
    return embeddings


def test_vector_store(embeddings, chunks):
    """Test the vector store."""
    print("\n=== Testing Vector Store ===")
    
    # Create vector store
    vector_store = FAISSVectorStore(embedding_dim=384)
    vector_store.create_index(embeddings, chunks)
    
    # Test search
    generator = EmbeddingGenerator()
    query = "What do customers think about delivery speed?"
    query_embedding = generator.generate_query_embedding(query)
    
    results = vector_store.search(query_embedding, k=3)
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}: Similarity={result['similarity_score']:.3f}, Chunk ID={result['chunk']['chunk_id']}")
    
    return vector_store


def test_rag_retriever():
    """Test the full RAG retriever."""
    print("\n=== Testing RAG Retriever ===")
    
    # Load reviews
    reviews_file = PROJECT_ROOT / "data" / "store" / "reviews_sampled_3000.json"
    reviews = load_json(reviews_file).get("reviews", [])
    
    # Use a small subset for testing
    test_reviews = reviews[:100]
    print(f"Testing with {len(test_reviews)} reviews")
    
    # Initialize retriever
    retriever = RAGRetriever()
    retriever.initialize_from_reviews(test_reviews, force_refresh=True)
    
    # Test retrieval
    query = "What do customers think about delivery speed?"
    results = retriever.retrieve_relevant_chunks(query, k=3)
    
    print(f"Retrieved {len(results)} chunks")
    for i, result in enumerate(results, 1):
        print(f"Result {i}: Similarity={result['similarity_score']:.3f}")
    
    # Test formatting
    formatted = retriever.format_retrieved_chunks(results)
    print(f"\nFormatted chunks length: {len(formatted)} characters")
    print(f"First 200 characters: {formatted[:200]}...")
    
    # Get system status
    status = retriever.get_system_status()
    print(f"\nSystem status: {status}")


if __name__ == "__main__":
    try:
        # Run tests
        chunks = test_chunking()
        embeddings = test_embeddings(chunks)
        vector_store = test_vector_store(embeddings, chunks[:10])
        test_rag_retriever()
        
        print("\n=== All Tests Passed ===")
    except Exception as e:
        print(f"\n=== Test Failed ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
