#!/usr/bin/env python3
"""
Search Anonymized CSV Data

This script allows you to search through anonymized CSV data by encoding your search terms
using the same hashing algorithm used during anonymization.
"""

import csv
import hashlib
from typing import List, Dict, Any

# Must match the settings from anonymize.py
HASH_LENGTH = 16


def encode_search_term(search_term: str) -> str:
    """
    Encode a search term using the same algorithm as anonymization.
    
    Args:
        search_term: The original value to search for
        
    Returns:
        Encoded hash that matches anonymized data
    """
    if not search_term or search_term.strip() == "":
        return ""
    
    # Apply the same processing as in anonymize_value()
    processed_value = search_term.strip().lower()
    hash_object = hashlib.sha256(processed_value.encode())
    return hash_object.hexdigest()[:HASH_LENGTH]


def search_csv(csv_file: str, column: str, search_term: str) -> List[Dict[str, Any]]:
    """
    Search for encoded values in anonymized CSV.
    
    Args:
        csv_file: Path to anonymized CSV file
        column: Column name to search in
        search_term: Original value to search for
        
    Returns:
        List of matching rows
    """
    encoded_term = encode_search_term(search_term)
    print(f"Searching for '{search_term}' -> encoded as '{encoded_term}'")
    
    matches = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, 1):
            if row.get(column) == encoded_term:
                row['_row_number'] = row_num
                matches.append(row)
    
    return matches


def search_multiple_terms(csv_file: str, search_queries: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Search for multiple terms across different columns.
    
    Args:
        csv_file: Path to anonymized CSV file
        search_queries: Dict mapping column names to search terms
        
    Returns:
        List of matching rows
    """
    encoded_queries = {}
    for column, term in search_queries.items():
        encoded_queries[column] = encode_search_term(term)
        print(f"Column '{column}': '{term}' -> '{encoded_queries[column]}'")
    
    matches = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, 1):
            match = True
            for column, encoded_term in encoded_queries.items():
                if row.get(column) != encoded_term:
                    match = False
                    break
            
            if match:
                row['_row_number'] = row_num
                matches.append(row)
    
    return matches


def search_contains(csv_file: str, search_queries: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Search for rows where any column contains the encoded search terms.
    
    Args:
        csv_file: Path to anonymized CSV file
        search_queries: Dict mapping column names to search terms (use '*' for any column)
        
    Returns:
        List of matching rows
    """
    encoded_queries = {}
    for column, term in search_queries.items():
        encoded_queries[column] = encode_search_term(term)
        print(f"Column '{column}': '{term}' -> '{encoded_queries[column]}'")
    
    matches = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, 1):
            for column, encoded_term in encoded_queries.items():
                if column == '*':
                    # Search in any column
                    if encoded_term in row.values():
                        row['_row_number'] = row_num
                        matches.append(row)
                        break
                else:
                    # Search in specific column
                    if row.get(column) == encoded_term:
                        row['_row_number'] = row_num
                        matches.append(row)
                        break
    
    return matches


# Example usage
if __name__ == "__main__":
    # Example searches
    csv_file = "out_anonymized.csv"
    
    print("=== Single Term Search ===")
    results = search_csv(csv_file, "name", "John Doe")
    print(f"Found {len(results)} matches")
    for result in results:
        print(f"Row {result['_row_number']}: {result}")
    
    print("\n=== Multiple Terms Search ===")
    multi_results = search_multiple_terms(csv_file, {
        "name": "Jane Smith",
        "city": "Los Angeles"
    })
    print(f"Found {len(multi_results)} matches")
    for result in multi_results:
        print(f"Row {result['_row_number']}: {result}")
    
    print("\n=== Search Any Column ===")
    any_results = search_contains(csv_file, {"*": "Chicago"})
    print(f"Found {len(any_results)} matches")
    for result in any_results:
        print(f"Row {result['_row_number']}: {result}")