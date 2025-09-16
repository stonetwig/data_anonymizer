#!/usr/bin/env python3
"""
Simple utility to encode search terms for anonymized data lookup.
"""

import hashlib

# Must match the settings from anonymize.py
HASH_LENGTH = 16

def encode(search_term: str) -> str:
    """
    Encode a search term to match anonymized data.
    
    Args:
        search_term: Original value to encode
        
    Returns:
        Encoded hash that matches anonymized data
    """
    if not search_term or search_term.strip() == "":
        return ""
    
    processed_value = search_term.strip().lower()
    hash_object = hashlib.sha256(processed_value.encode())
    return hash_object.hexdigest()[:HASH_LENGTH]

# Command line usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:])
        encoded = encode(term)
        print(f"'{term}' -> '{encoded}'")
    else:
        print("Usage: python encode_search.py <search_term>")
        print("Example: python encode_search.py 'John Doe'")