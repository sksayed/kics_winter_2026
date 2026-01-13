#!/usr/bin/env python3
"""
PDF Text Extraction Script

Extracts text from PDF files and saves it to text files.
Usage:
    python extract_pdf_text.py [pdf_filename]
    If no filename is provided, processes all PDF files in the current directory.
"""

import sys
import os
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf library is not installed.")
    print("Please install it using: pip install pypdf")
    sys.exit(1)


def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        reader = PdfReader(pdf_path)
        text = []
        
        print(f"Processing {pdf_path.name}...")
        print(f"Number of pages: {len(reader.pages)}")
        
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            text.append(page_text)
            print(f"  Extracted text from page {page_num}")
        
        return "\n".join(text)
    
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return None


def save_text_to_file(text, output_path):
    """
    Save extracted text to a file.
    
    Args:
        text: Text content to save
        output_path: Path to save the text file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Text saved to: {output_path}")
    except Exception as e:
        print(f"Error saving text to {output_path}: {str(e)}")


def main():
    """Main function to handle PDF text extraction."""
    current_dir = Path('.')
    
    # If a PDF filename is provided as argument
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        if not pdf_file.exists():
            print(f"Error: File '{pdf_file}' not found.")
            sys.exit(1)
        
        if not pdf_file.suffix.lower() == '.pdf':
            print(f"Error: '{pdf_file}' is not a PDF file.")
            sys.exit(1)
        
        pdf_files = [pdf_file]
    else:
        # Process all PDF files in the current directory
        pdf_files = list(current_dir.glob('*.pdf'))
        
        if not pdf_files:
            print("No PDF files found in the current directory.")
            sys.exit(1)
        
        print(f"Found {len(pdf_files)} PDF file(s) to process.\n")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        print(f"\n{'='*60}")
        print(f"Processing: {pdf_file.name}")
        print(f"{'='*60}")
        
        # Extract text
        text = extract_text_from_pdf(pdf_file)
        
        if text:
            # Create output filename
            output_file = pdf_file.with_suffix('.txt')
            
            # Save to text file
            save_text_to_file(text, output_file)
            print(f"Successfully extracted {len(text)} characters from {pdf_file.name}")
        else:
            print(f"Failed to extract text from {pdf_file.name}")
        
        print()


if __name__ == "__main__":
    main()






