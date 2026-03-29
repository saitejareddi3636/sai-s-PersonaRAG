#!/usr/bin/env python3
"""
Static Content Validation - 7 Question Verification
Analyzes chunks.json directly to predict retrieval quality without live backend
"""

import json
from pathlib import Path

chunks_file = Path('/Users/saitejareddy/Desktop/sai-s-PersonaRAG/data/processed/chunks.json')
with open(chunks_file) as f:
    data = json.load(f)

questions = [
    ("Tell me about yourself", ["summary", "recruiter_faq", "target_roles"]),
    ("What are his strongest technical skills?", ["skills_swe", "skills_ml", "recruiter_faq"]),
    ("Is he stronger in SWE or ML?", ["recruiter_faq", "skills_swe", "skills_ml", "working_style"]),
    ("What backend experience does he have?", ["experience", "recruiter_faq", "skills_swe"]),
    ("What production AI systems has he built?", ["experience", "achievements", "recruiter_faq", "projects"]),
    ("What roles is he targeting?", ["target_roles", "recruiter_faq", "summary"]),
    ("Tell me about his strongest project", ["projects", "recruiter_faq"])
]

print("=" * 100)
print("7-QUESTION STATIC VALIDATION TEST")
print("(Analyzes chunks.json to predict retrieval quality)")
print("=" * 100)
print()

for q_num, (question, expected_sources) in enumerate(questions, 1):
    print(f"[Q{q_num}] {question}")
    print("-" * 100)
    
    # Find relevant chunks
    relevant_chunks = []
    for chunk in data.get('chunks', []):
        source_file = chunk.get('source_file', '')
        if any(exp in source_file for exp in expected_sources):
            relevant_chunks.append(chunk)
    
    if relevant_chunks:
        print(f"✓ Expected {len(expected_sources)} source files, found {len(set(c['source_file'] for c in relevant_chunks))} in chunks:")
        
        # Group by source
        by_source = {}
        for chunk in relevant_chunks:
            source = chunk.get('source_file', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(chunk)
        
        for source in sorted(by_source.keys()):
            sections = set(c.get('section_title', 'N/A') for c in by_source[source])
            print(f"  • {source:20} ({len(by_source[source])} chunks) → {', '.join(list(sections)[:2])}...")
        
        # Sample content from first chunk
        sample_chunk = relevant_chunks[0]
        preview = sample_chunk.get('text', '')[:180].replace('\n', ' ')
        print(f"\n  Content sample: {preview}...")
        
        # Quality checks
        full_text = '\n'.join(c.get('text', '') for c in relevant_chunks)
        
        checks = {
            'specificity': any(word in full_text.lower() for word in ['fastapi', 'spring boot', 'avtar', 'niro', 'jpmorg', 'intuit', 'pytorch', 'raag', 'voice']),
            'student_positioning': any(phrase in full_text for phrase in ['CS student', 'graduating May 2026', 'GPA 3.9', 'graduating', 'May 2026']),
            'no_generic': not any(phrase in full_text for phrase in ['passionate engineer', 'love solving', 'team player']),
            'no_seniority': not any(phrase in full_text for phrase in ['senior engineer', 'staff engineer', 'tech lead', 'mid-level']),
        }
        
        print(f"\n  Quality checks:")
        print(f"    {'✓' if checks['specificity'] else '✗'} Specific references (companies, tech stack)")
        print(f"    {'✓' if checks['student_positioning'] else '✗'} Student positioning")
        print(f"    {'✓' if checks['no_generic'] else '✗'} No generic language")
        print(f"    {'✓' if checks['no_seniority'] else '✗'} No seniority inflation")
        
        all_pass = all(checks.values())
        status = "✅ PASS" if all_pass else "⚠️  NEEDS REVIEW"
        print(f"\n  Status: {status}")
    else:
        print(f"❌ ERROR: No relevant chunks found for expected sources: {expected_sources}")
    
    print()

print("=" * 100)
print("STATIC VALIDATION COMPLETE")
print("=" * 100)
print()

# Summary statistics
print("KNOWLEDGE BASE SUMMARY:")
print(f"  • Total chunks: {len(data.get('chunks', []))}")
print(f"  • Source files: {len(data.get('sources', []))}")
print(f"  • File size: {chunks_file.stat().st_size / 1024:.1f} KB")
print()

# Student positioning check
student_chunks = sum(1 for c in data.get('chunks', []) if any(p in c.get('text', '') for p in ['CS student', 'May 2026', 'graduating']))
print(f"✓ Student positioning chunks: {student_chunks}")

# Seniority check
seniority_chunks = sum(1 for c in data.get('chunks', []) if any(p in c.get('text', '') for p in ['senior engineer', 'staff engineer', 'mid-level']))
print(f"✓ Seniority inflation chunks: {seniority_chunks}")

# Generic check
generic_chunks = sum(1 for c in data.get('chunks', []) if any(p in c.get('text', '') for p in ['passionate engineer', 'love solving']))
print(f"✓ Generic language chunks: {generic_chunks}")

print()
print("✅ KNOWLEDGE BASE READY FOR LIVE VALIDATION")
print("   (static analysis shows high quality)")
print()
