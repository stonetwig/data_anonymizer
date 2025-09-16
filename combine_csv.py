#!/usr/bin/env python3
"""
CSV Combiner Script

This script reads multiple CSV files from a configured directory and combines them into one
consolidated CSV file called 'out.csv'. It handles case-insensitive column matching, meaning 
columns with different cases (e.g., 'Name', 'NAME', 'name') will be treated as the same column.

Configuration:
    INPUT_FOLDER: Directory containing CSV files to combine
    OUTPUT_FILE: Output file name (always 'out.csv')
"""

# CONFIGURATION - Change this path to your desired input folder
INPUT_FOLDER = "/home/markus/Documents/leaks/miljodata"  # Current directory - change to your CSV folder path
OUTPUT_FILE = "out.csv"

import csv
import os
import sys
import glob
import chardet
from collections import OrderedDict
from typing import List, Dict, Set


def detect_encoding(file_path: str) -> str:
    """Detect the encoding of a file."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'


def normalize_column_name(col_name: str) -> str:
    """Normalize column name to lowercase for case-insensitive comparison."""
    return str(col_name).lower().strip()


def get_unified_columns(csv_files: List[str]) -> Dict[str, str]:
    """
    Analyze all CSV files and create a mapping of normalized column names
    to their preferred representation (first occurrence).
    
    Returns:
        Dict mapping normalized column names to their preferred representation
    """
    column_mapping = OrderedDict()
    
    for csv_file in csv_files:
        try:
            encoding = detect_encoding(csv_file)
            with open(csv_file, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                if header:
                    for col in header:
                        normalized = normalize_column_name(col)
                        if normalized not in column_mapping:
                            column_mapping[normalized] = col
                    
        except Exception as e:
            print(f"Warning: Could not read {csv_file}: {e}")
            
    return column_mapping


def read_csv_data(csv_file: str, column_mapping: Dict[str, str]) -> List[Dict[str, str]]:
    """
    Read CSV data and normalize column names according to the mapping.
    
    Returns:
        List of dictionaries representing rows with normalized column names
    """
    data = []
    
    try:
        encoding = detect_encoding(csv_file)
        with open(csv_file, 'r', encoding=encoding, newline='') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Create new row with unified column names
                unified_row = {}
                
                # Initialize all columns with empty strings
                for normalized, unified_name in column_mapping.items():
                    unified_row[unified_name] = ""
                
                # Map existing data to unified columns
                for original_col, value in row.items():
                    normalized = normalize_column_name(original_col)
                    if normalized in column_mapping:
                        unified_name = column_mapping[normalized]
                        unified_row[unified_name] = value or ""
                
                data.append(unified_row)
                
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        
    return data


def combine_csv_files():
    """
    Combine multiple CSV files into one with case-insensitive column matching.
    Uses the configured INPUT_FOLDER and OUTPUT_FILE variables.
    """
    
    # Delete existing output file if it exists
    output_path = os.path.join(INPUT_FOLDER, OUTPUT_FILE)
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Deleted existing {OUTPUT_FILE}")
    
    # Find all CSV files in the directory
    csv_pattern = os.path.join(INPUT_FOLDER, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        print(f"No CSV files found in directory: {INPUT_FOLDER}")
        return
    
    print(f"Found {len(csv_files)} CSV files:")
    for csv_file in csv_files:
        print(f"  - {os.path.basename(csv_file)}")
    
    # Get unified column structure
    print("\nAnalyzing column structure...")
    column_mapping = get_unified_columns(csv_files)
    
    if not column_mapping:
        print("No valid columns found in any CSV files.")
        return
    
    print(f"Found {len(column_mapping)} unique columns (case-insensitive):")
    for normalized, original in column_mapping.items():
        print(f"  - {original}")
    
    # Combine all CSV files
    all_data = []
    total_rows = 0
    
    for csv_file in csv_files:
        print(f"\nProcessing: {os.path.basename(csv_file)}")
        
        # Show column mapping for this file
        try:
            encoding = detect_encoding(csv_file)
            print(f"  Detected encoding: {encoding}")
            with open(csv_file, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                header = next(reader, None)
                
                if header:
                    for col in header:
                        normalized = normalize_column_name(col)
                        if normalized in column_mapping:
                            unified_name = column_mapping[normalized]
                            if col != unified_name:
                                print(f"  Mapped '{col}' -> '{unified_name}'")
                            else:
                                print(f"  Keeping '{col}'")
        except Exception as e:
            print(f"  Error reading header: {e}")
            continue
        
        # Read and process data
        file_data = read_csv_data(csv_file, column_mapping)
        all_data.extend(file_data)
        total_rows += len(file_data)
        print(f"  Added {len(file_data)} rows")
    
    if not all_data:
        print("No data could be processed from any CSV files.")
        return
    
    # Write combined CSV
    print(f"\nCombining data from {len(csv_files)} files...")
    
    # Get ordered column names
    unified_columns = list(column_mapping.values())
    
    try:
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=unified_columns)
            writer.writeheader()
            writer.writerows(all_data)
        
        print(f"\nCombined CSV saved as: {output_path}")
        print(f"Total rows: {len(all_data)}")
        print(f"Total columns: {len(unified_columns)}")
        
        # Show a preview
        print("\nPreview of combined data (first 5 rows):")
        print("Columns:", ", ".join(unified_columns))
        for i, row in enumerate(all_data[:5]):
            values = [row.get(col, "") for col in unified_columns]
            print(f"Row {i+1}: {values}")
            
    except Exception as e:
        print(f"Error writing combined CSV: {e}")


def main():
    """Main function to run the CSV combiner."""
    
    # Validate input directory
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: Directory '{INPUT_FOLDER}' does not exist.")
        sys.exit(1)
    
    print(f"Input directory: {INPUT_FOLDER}")
    print(f"Output file: {OUTPUT_FILE}")
    print("=" * 50)
    
    try:
        combine_csv_files()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
