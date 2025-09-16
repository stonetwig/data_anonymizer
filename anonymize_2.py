#!/usr/bin/env python3
import hashlib
import sys

def anonymize_value(value):
    """Anonymize a value using SHA256 hash"""
    return hashlib.sha256(value.strip().lower().encode()).hexdigest()

def process_file(input_file, output_file=None):
    """Process the input file and anonymize each line"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        anonymized_lines = []
        
        for line in lines:
            line = line.rstrip('\n\r')
            if not line:
                anonymized_lines.append('')
                continue
            
            parts = line.split('#')
            anonymized_parts = [anonymize_value(part) for part in parts]
            anonymized_line = '#'.join(anonymized_parts)
            anonymized_lines.append(anonymized_line)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for line in anonymized_lines:
                    f.write(line + '\n')
        else:
            for line in anonymized_lines:
                print(line)
                
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python anonymize_2.py <input_file> [output_file]")
        print("If no output file is specified, results will be printed to stdout")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    process_file(input_file, output_file)