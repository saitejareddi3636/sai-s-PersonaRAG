#!/usr/bin/env python3
"""
Verify that the PersonaRAG knowledge base is working end-to-end.
Tests retrieval and answer generation with sample questions.
"""
import os
import sys
import asyncio

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.rag.retrieve import retriever
from app.services.llm_service import answer_generator
from app.core.config import settings

async def test_query(question: str):
    """Test a single query through the system."""
    print(f"\n{'='*70}")
    print(f"Question: {question}")
    print(f"{'='*70}")
    
    # Retrieve relevant chunks
    retrieved = await retriever.retrieve(question, top_k=3)
    
    print(f"\nRetrieved {len(retrieved)} chunks:")
    for i, chunk in enumerate(retrieved, 1):
        source = chunk.get("source_file", "unknown")
        section = chunk.get("section_title", "N/A")
        score = chunk.get("score", 0)
        print(f"\n  {i}. {source} > {section} (score: {score:.3f})")
        text_preview = chunk.get("text", "")[:100]
        print(f"     {text_preview}...")
    
    # Generate answer
    context = "\n\n".join([chunk.get("text", "") for chunk in retrieved])
    answer = await answer_generator.generate(question, context)
    
    print(f"\nAnswer: {answer['answer']}")
    print(f"Confidence: {answer['confidence']}")
    
    # Show citations
    if answer.get('sources'):
        print(f"Sources: {', '.join(answer['sources'])}")

async def main():
    """Run end-to-end verification tests."""
    print("PersonaRAG Knowledge Base Verification")
    print("=" * 70)
    print(f"Chunks loaded: {settings.CHUNKS_JSON_PATH}")
    print(f"Retrieval backend: {settings.RETRIEVAL_BACKEND}")
    print(f"LLM: {settings.OPENAI_MODEL}")
    
    # Test queries
    test_queries = [
        "What is your backend experience?",
        "Tell me about your RAG and AI projects",
        "What roles are you targeting?",
        "What's your working style and approach to debugging?",
        "What programming languages do you know?",
    ]
    
    for query in test_queries:
        try:
            await test_query(query)
        except Exception as e:
            print(f"Error processing query: {e}")
    
    print(f"\n{'='*70}")
    print("Verification complete!")
    print(f"{'='*70}")

if __name__ == "__main__":
    asyncio.run(main())
