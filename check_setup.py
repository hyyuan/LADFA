"""
Setup Verification Script

Simple script to check if all prerequisites for the framework are in place.
Run this before attempting to analyze privacy policies.
"""

import os
from pathlib import Path


def check_prerequisites():
    """
    Check if required files and dependencies exist.
    Returns True if all prerequisites are met.
    """
    print("\n=== Checking Prerequisites ===\n")
    
    issues = []
    
    # Check for API key
    if not os.path.exists('GROQ_API_KEY'):
        issues.append("❌ GROQ_API_KEY file not found")
        print("❌ GROQ API key file not found")
    else:
        print("✓ GROQ API key file found")
    
    # Check for knowledge bases
    kb_files = [
        'kb/data_categories_kt.json',
        'kb/data_consumer_type_kt.json',
        'kb/data_processing_purpose_kt.json',
        'kb/data_processing_method_kt.json'
    ]
    
    for kb_file in kb_files:
        if not os.path.exists(kb_file):
            issues.append(f"❌ Knowledge base missing: {kb_file}")
            print(f"❌ Knowledge base missing: {kb_file}")
        else:
            print(f"✓ Knowledge base found: {kb_file}")
    
    # Check for input data
    data_files = list(Path('data').glob('*.html')) + list(Path('data').glob('*.htm')) + list(Path('data').glob('*.pdf'))
    if not data_files:
        issues.append("⚠️  No privacy policy files found in data/ directory")
        print("⚠️  No privacy policy files found in data/ directory")
    else:
        print(f"✓ Found {len(data_files)} privacy policy file(s) in data/")
    
    # Check for required Python packages
    try:
        import groq
        print("✓ groq package installed")
    except ImportError:
        issues.append("❌ groq package not installed")
        print("❌ groq package not installed")
    
    try:
        import llama_index
        print("✓ llama_index package installed")
    except ImportError:
        issues.append("❌ llama_index package not installed")
        print("❌ llama_index package not installed")
    
    try:
        import spacy
        print("✓ spacy package installed")
        try:
            spacy.load("en_core_web_sm")
            print("✓ spaCy en_core_web_sm model installed")
        except OSError:
            issues.append("❌ spaCy model en_core_web_sm not installed")
            print("❌ spaCy model en_core_web_sm not installed")
    except ImportError:
        issues.append("❌ spacy package not installed")
        print("❌ spacy package not installed")
    
    if issues:
        print("\n=== Issues Found ===")
        for issue in issues:
            print(issue)
        print("\n💡 See README.md for setup instructions")
        return False
    
    print("\n✓ All prerequisites met! You're ready to analyze privacy policies.")
    return True


if __name__ == "__main__":
    check_prerequisites()
