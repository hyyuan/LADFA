"""
HTML to Text Extraction Module

This module provides functionality to parse HTML files and extract structured text content.
It handles headers, paragraphs, lists, tables, and applies various segmentation strategies
to create meaningful text chunks suitable for further processing.
"""

from bs4 import BeautifulSoup
import re


def remove_header_and_footer(soup):
    """
    Remove header, footer, and script tags from the HTML soup object.
    
    Args:
        soup (BeautifulSoup): Parsed HTML document
        
    Returns:
        BeautifulSoup: Modified soup object with headers/footers removed
    """
    for header in soup.find_all(['header', 'footer', 'script']):
        header.decompose()
    return soup


def read_html_from_file(file_path):
    """
    Read HTML content from a file.
    
    Args:
        file_path (str): Path to the HTML file
        
    Returns:
        str: HTML content as a string
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    return html_content


def get_starting_index(rows):
    """
    Find the first non-empty row in a table to use as the starting index.
    
    Args:
        rows (list): List of table row elements
        
    Returns:
        int: Index of the first non-empty row
    """
    for i in range(0, len(rows)):
        tmp_row = rows[i]
        row_segments = []
        for cell in tmp_row.find_all(['td', 'th']):
            cell_contents = [
                item.strip() 
                for item in cell.get_text(separator="|").split('|') 
                if item.strip()
            ]
            row_segments.append(', '.join(cell_contents))
        if row_segments:
            return i
        else:
            continue


def get_row_text(row_segments, row):
    """
    Extract text from a table row and append to row_segments list.
    
    Args:
        row_segments (list): List to append row text to
        row (BeautifulSoup element): Table row element
        
    Returns:
        list: Updated row_segments list
    """
    for cell in row.find_all(['td', 'th']):
        cell_contents = [
            item.strip() 
            for item in cell.get_text(separator="|").split('|') 
            if item.strip()
        ]
        row_segments.append(', '.join(cell_contents))
    return row_segments


def extract_tables_v2(soup):
    """
    Extract table data with title row handling.
    
    Each data row is paired with the table's title row for context,
    and marked with '_table_' prefix.
    
    Args:
        soup (BeautifulSoup): Parsed HTML document
        
    Returns:
        list: List of formatted table row strings with titles
    """
    segments = []
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        starting_idx = get_starting_index(rows)
        title_row = rows[starting_idx]
        
        # Process data rows (after title row)
        for i in range(starting_idx + 1, len(rows)):
            row = rows[i]
            row_segments = []
            
            # Add title row content first
            row_segments = get_row_text(row_segments, title_row)
            row_segments.append('\n')
            
            # Add data row content
            for cell in row.find_all(['td', 'th']):
                cell_contents = [
                    item.strip() 
                    for item in cell.get_text(separator="|").split('|') 
                    if item.strip()
                ]
                row_segments.append(', '.join(cell_contents))

            # Mark as table data and join segments
            if row_segments:
                segments.append(f"_table_ {' | '.join(row_segments)}")
    return segments


def extract_content_from_html(html_content):
    """
    Extract structured text content from HTML, excluding links.
    
    Processes paragraphs, headings (h1-h5), and list items. Headers are
    marked with asterisks based on level. Excludes elements containing links.
    
    Args:
        html_content (str): HTML content as string
        
    Returns:
        tuple: (extracted_text as string, BeautifulSoup object)
    """
    soup = BeautifulSoup(html_content, "html.parser")
    remove_header_and_footer(soup)
    texts = []

    def process_element(element):
        """Process individual HTML elements and extract text."""
        # Skip elements inside tables (handled separately)
        if element.find_parent('table') is None:
            if element.name == 'p':
                # Extract paragraph text, excluding links
                text = ''.join(
                    child.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                    for child in element.contents if child.name != 'a'
                )
                if text.strip():
                    texts.append(text)
            elif element.name == 'h1':
                text = element.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                if text:
                    texts.append('***** ' + text)  # Level 1 heading
            elif element.name == 'h2':
                text = element.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                if text:
                    texts.append('**** ' + text)  # Level 2 heading
            elif element.name == 'h3':
                text = element.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                if text:
                    texts.append('*** ' + text)  # Level 3 heading
            elif element.name == 'h4':
                text = element.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                if text:
                    texts.append('** ' + text)  # Level 4 heading
            elif element.name == 'h5':
                text = element.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                if text:
                    texts.append('* ' + text)  # Level 5 heading
            elif element.name == 'li':
                # Extract list items, excluding those with links
                if not element.find('a'):
                    text = element.get_text(separator=' ', strip=True).replace('\xa0', ' ')
                    if text:
                        texts.append('- ' + text)
            elif element.name in ['ul', 'ol']:
                # Process list items recursively
                for child in element.find_all('li', recursive=False):
                    process_element(child)

    # Process top-level elements only
    for element in soup.find_all(True):
        if element.name in ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li', 'ol', 'ul']:
            if not element.find_parents(['ol', 'ul']):
                process_element(element)

    return "\n".join(texts), soup


def extract_bullet_points(paragraph):
    """
    Extract bullet point symbols from the start of a paragraph.
    
    Args:
        paragraph (str): Paragraph text
        
    Returns:
        str: Bullet point symbol or empty string if none found
    """
    # Pattern to match various bullet point symbols
    bullet_point_patterns = r'^([*\-+•o•>\s<·\\,.\-]+)\s+'
    bullet_points = re.findall(bullet_point_patterns, paragraph, re.MULTILINE)
    return bullet_points[0] if bullet_points else ''


def merge_paragraphs_by_bullet_points(paragraphs):
    """
    Group consecutive paragraphs with the same bullet point style together.
    
    Args:
        paragraphs (list): List of paragraph strings
        
    Returns:
        list: List of merged paragraph groups
    """
    grouped = []
    current_group = []
    current_symbol = None

    for para in paragraphs:
        symbol = extract_bullet_points(para)

        if symbol == current_symbol or not symbol:
            current_group.append(para)
            if not symbol:
                # Paragraph without bullets - treat as standalone
                grouped.append('\n\n'.join(current_group))
                current_group = []
                current_symbol = None
        else:
            # New bullet style - start new group
            if current_group:
                grouped.append('\n\n'.join(current_group))
            current_group = [para]
            current_symbol = symbol

    # Add final group if exists
    if current_group:
        grouped.append('\n\n'.join(current_group))

    return grouped


def filter_and_further_segment(input_text):
    """
    Further segment text by splitting into paragraphs and merging by bullet points.
    
    Args:
        input_text (str): Input text to segment
        
    Returns:
        list: List of segmented text chunks
    """
    final_segments = []

    # Split into individual paragraphs
    paragraphs = [para.strip() for para in input_text.split('\n') if para.strip()]

    # Merge paragraphs with same bullet style
    merged_paragraphs = merge_paragraphs_by_bullet_points(paragraphs)

    final_segments.extend(merged_paragraphs)
    return final_segments


def merge_segments_ending_with_colon(segments):
    """
    Merge segments ending with ':' with their following segment.
    
    This handles cases where a heading or introduction ends with a colon
    and should be combined with the next paragraph.
    
    Args:
        segments (list): List of text segments
        
    Returns:
        list: List of merged segments
    """
    merged_segments = []
    i = 0

    while i < len(segments):
        current_segment = segments[i]

        if current_segment.endswith(':') and (i + 1) < len(segments):
            # Merge with next segment
            next_segment = segments[i + 1]
            merged_segment = f"{current_segment}\n\n{next_segment}"
            merged_segments.append(merged_segment)
            i += 2  # Skip the next segment
        else:
            merged_segments.append(current_segment)
            i += 1

    return merged_segments


def discard_short_segments(segments, min_length=50):
    """
    Filter out segments shorter than the minimum length.
    
    Removes very short segments that are likely just headings or
    fragments rather than meaningful content.
    
    Args:
        segments (list): List of text segments
        min_length (int): Minimum length threshold
        
    Returns:
        list: Filtered list of segments
    """
    refined_segments = []
    for segment in segments:
        if len(segment) >= min_length:
            # Remove '=' characters and add to refined list
            segment = segment.replace("=", "")
            refined_segments.append(segment)
    return refined_segments


def separate_long_segments(segments, max_length=1000):
    """
    Split very long segments into individual lines.
    
    Args:
        segments (list): List of text segments
        max_length (int): Maximum length threshold
        
    Returns:
        list: List with long segments split into lines
    """
    new_segments = []
    for segment in segments:
        if len(segment) <= max_length:
            new_segments.append(segment)
        else:
            # Split long segment into individual lines
            lines = segment.split('\n')
            for line in lines:
                new_segments.append(line)
    return new_segments


def extract_and_process_text_from_file(file_path):
    """
    Main function to extract and process text from an HTML file.
    
    Performs complete pipeline: read HTML, extract content, segment text,
    merge related segments, filter by length, and extract tables.
    
    Args:
        file_path (str): Path to the HTML file
        
    Returns:
        list: List of processed text segments ready for analysis
    """
    # Step 1: Read HTML content from file
    html_content = read_html_from_file(file_path)

    if html_content:
        # Step 2: Clean HTML and extract text content
        extracted_text, soup = extract_content_from_html(html_content)

        # Step 3: Further segment based on paragraphs and bullet points
        filtered_segments = filter_and_further_segment(extracted_text)

        # Step 4: Merge segments ending with ':' with next segment
        merged_segments = merge_segments_ending_with_colon(filtered_segments)

        # Step 5: Separate very long segments (>10000 chars)
        segments = separate_long_segments(merged_segments, 10000)

        # Step 6: Discard very short segments (<50 chars)
        final_segments = discard_short_segments(segments)

        # Step 7: Extract and add table data
        table_segments = extract_tables_v2(soup)
        final_segments.extend(table_segments)

        return final_segments
    else:
        return []
