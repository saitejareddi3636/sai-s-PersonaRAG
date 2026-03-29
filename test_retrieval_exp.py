import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load chunks
with open('data/processed/chunks.json', 'r') as f:
    data = json.load(f)
chunks = data['chunks']

# Build TF-IDF
texts = [c['text'] for c in chunks]
vectorizer = TfidfVectorizer(max_features=8192, stop_words="english", ngram_range=(1, 2))
matrix = vectorizer.fit_transform(texts)

# Test queries
queries = ["how many years work experience", "tell me about yourself", "work experience"]

for query in queries:
    q_vec = vectorizer.transform([query])
    scores = cosine_similarity(q_vec, matrix).ravel()
    
    # Get top 3
    top_indices = np.argsort(-scores)[:3]
    print(f"\n{'='*60}")
    print(f"Query: '{query}'")
    print('='*60)
    for i, idx in enumerate(top_indices):
        chunk = chunks[idx]
        print(f"\n#{i+1} Score: {scores[idx]:.4f}")
        print(f"    Source: {chunk['source_file']}")
        print(f"    Section: {chunk['section_title']}")
        print(f"    Text: {chunk['text'][:100]}...")
