"""
PDF Text Extraction Module

This module provides functionality to extract and chunk text content from PDF files
based on numbered sub-headings and paragraph breaks.
"""

import pypdf


def split_pdf(pdf_path):
    """
    Split a PDF file into chunks based on numbered sub-headings and paragraph breaks.
    
    This function reads a PDF file and splits its content into logical chunks,
    using numbered headings as primary delimiters and paragraph breaks as
    secondary delimiters.
    
    Args:
        pdf_path (str): Path to the PDF file to process
        
    Returns:
        list: List of text content chunks extracted from the PDF
    """
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        pdf_reader = pypdf.PdfReader(file)

        chunks = []
        current_chunk = []
        current_heading_num = 0

        # Iterate through all pages in the PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            # Split the text by lines for processing
            lines = text.split('\n')

            # Process each line
            for line in lines:
                # Check if the line is a numbered sub-heading (e.g., "1.", "2.", etc.)
                if line.startswith(str(current_heading_num + 1) + '.'):
                    # Save the current chunk if it has content
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                        current_chunk = []

                    # Update to the new heading number
                    current_heading_num += 1

                # Add the line to the current chunk
                current_chunk.append(line)

                # If we encounter a blank line, treat it as a paragraph break
                if not line.strip():
                    if current_chunk:
                        chunks.append('\n'.join(current_chunk))
                        current_chunk = []

        # Add any remaining content as the final chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks
