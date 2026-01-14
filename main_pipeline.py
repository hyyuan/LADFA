"""
Main Privacy Policy Analysis Pipeline

This script orchestrates the complete privacy policy analysis workflow:
1. Converts HTML/PDF privacy policies to segmented text
2. Identifies data flows using LLM analysis
3. Categorizes data types, collection parties, purposes, and methods
4. Outputs structured results to CSV files

The pipeline uses RAG (Retrieval Augmented Generation) with knowledge bases
for accurate categorization of privacy policy elements.
"""

import time
import csv
import json
import os
import html2text as h2t
import groq_client as groq_client
import rag as rag
import agent_llm as agent
import pdf2text as pdfreader


def llm_pipeline(input_file):
    """
    Main pipeline function to process a privacy policy file.
    
    Workflow:
    1. Parse HTML/PDF to text segments
    2. Load and index knowledge bases (data types, parties, purposes, methods)
    3. For each segment:
       - Identify data flows using LLM
       - Categorize data types against KB
       - Categorize collection parties, purposes, and methods
    4. Write results to CSV
    
    Args:
        input_file (str): Path to input HTML or PDF privacy policy file
    """

    def write_row(row, num_rows):
        """
        Write a row to CSV if it has the correct number of columns.
        
        Args:
            row (list): Row data to write
            num_rows (int): Expected number of columns
        """
        if len(row) == num_rows:
            writer.writerow(row)
        else:
            print(f"Each row must have exactly {num_rows} columns")

    # Initialize Groq API client
    client = groq_client.getGroqClient('GROQ_API_KEY')

    # Determine file type and set up output paths
    file_name, file_extension = os.path.splitext(input_file)

    # Step 1: Process HTML/PDF and convert to text segmentation
    processed_segments = []
    if file_extension == '.html' or file_extension == '.htm':
        processed_segments = h2t.extract_and_process_text_from_file(input_file)
    elif file_extension == '.pdf':
        processed_segments = pdfreader.split_pdf(input_file)

    segment_output = file_name + '_segment.csv'

    # Write text segments to CSV for reference
    with open(segment_output, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(['index', 'text'])  # Header

        for i in range(0, len(processed_segments)):
            write_row([str(i), processed_segments[i]], 2)

    # Step 2: Initialize output CSV for results
    results_output = file_name + '_output.csv'
    with open(results_output, mode='w', newline='', encoding="utf-8") as file:

        writer = csv.writer(file)
        writer.writerow([
            'text_idx', 
            'data_type', 
            'data_category', 
            'data_flow', 
            'data_collection_party', 
            'data_collection_purpose', 
            'data_collection_method'
        ])

        # Step 3: Preprocess and index knowledge bases
        
        # Personal data types KB
        json_file_path = 'kb/data_categories_kt.json'
        documents = rag.convert_json(json_file_path)
        person_index = rag.indexingHuggingfaceEmbedding(
            documents, 
            'data_categories_index/',
            "BAAI/bge-small-en-v1.5"
        )
        # Create quick lookup dictionary for data types
        personal_data_dict = rag.json_to_dict(json_file_path)

        # Collection parties KB (data consumer types)
        json_file_path = 'kb/data_consumer_type_kt.json'
        documents = rag.convert_json(json_file_path)
        party_index = rag.indexingHuggingfaceEmbedding(
            documents, 
            'data_consumer_index/',
            "BAAI/bge-small-en-v1.5"
        )

        # Collection purposes KB (data processing purposes)
        json_file_path = 'kb/data_processing_purpose_kt.json'
        documents = rag.convert_json(json_file_path)
        purpose_index = rag.indexingHuggingfaceEmbedding(
            documents, 
            'data_processing_purpose_index/',
            "BAAI/bge-small-en-v1.5"
        )

        # Collection methods/types KB (data processing methods)
        json_file_path = 'kb/data_processing_method_kt.json'
        documents = rag.convert_json(json_file_path)
        collection_type_index = rag.indexingHuggingfaceEmbedding(
            documents, 
            'data_processing_method_index/',
            "BAAI/bge-small-en-v1.5"
        )

        # Dictionary to cache data type categorizations
        data_category_dict = {}

        # Step 4: Process each text segment
        for i in range(0, len(processed_segments)):
            idx = i
            text_segment = processed_segments[idx]
            print(f"Segment {i + 1}:\n{text_segment}\n")
            
            try:
                # Task 1: Filter relevant paragraphs and identify data flows
                num_tokens, data_flow_json = agent.selecting_paragraph_get_data_flows(
                    client, 
                    text_segment, 
                    modelID="llama-3.3-70b-versatile"
                )
                time.sleep(5)  # Rate limiting

                # Process only if data flows were found
                if data_flow_json != 'NO':
                    data_flows = json.loads(data_flow_json)

                    # Convert data flows to standardized format
                    data_flow_array = []
                    for data_flow_ in data_flows:
                        data_sender = data_flow_['data_sender']
                        data_types = data_flow_['data_type']
                        data_receivers = data_flow_['data_receiver']
                        
                        # Create individual flows for each data type
                        for data_type in data_types:
                            if isinstance(data_receivers, list):
                                # Multiple receivers - create flow for each
                                for data_receiver in data_receivers:
                                    data_flow_array.append(f"""
                                    {{ "data": [ {{ "data_sender": "{data_sender}", "data_type": "{data_type}", "data_receiver": "{data_receiver}" }} ] }}
                                    """)
                            else:
                                # Single receiver
                                data_flow_array.append(f"""
                                {{ "data": [ {{ "data_sender": "{data_sender}", "data_type": "{data_type}", "data_receiver": "{data_receivers}" }} ] }}
                                """)

                    # Retrieve context for categorization tasks
                    collection_response = rag.retrieving(purpose_index, text_segment)
                    party_responses = rag.retrieving(party_index, text_segment)
                    
                    # Prepare extended context for method categorization (include adjacent segments)
                    if idx - 1 >= 0 and idx + 1 < len(processed_segments):
                        prev_text = processed_segments[idx - 1]
                        after_text = processed_segments[idx + 1]
                        text_segment_method = prev_text + '\n' + text_segment + '\n' + after_text
                    elif idx - 1 < 0:
                        after_text = processed_segments[idx + 1]
                        text_segment_method = text_segment + '\n' + after_text
                    elif idx - 1 >= 0 and idx + 1 >= len(processed_segments):
                        prev_text = processed_segments[idx - 1]
                        text_segment_method = prev_text + '\n' + text_segment
                    else:
                        text_segment_method = text_segment

                    method_responses = rag.retrieving(collection_type_index, text_segment_method)

                    # Process each identified data flow
                    for data_flow in data_flow_array:
                        print('--------Processing data flow ' + str(data_flow))
                        data_flow_json = json.loads(data_flow)
                        data_flow_content = data_flow_json['data'][0]
                        data_sender = data_flow_content['data_sender']
                        data_type = data_flow_content['data_type']
                        data_receiver = data_flow_content['data_receiver']

                        # Task 2: Categorize data type
                        data_type_lower = data_type.lower()
                        if data_type_lower in personal_data_dict:
                            # Direct match in dictionary - fast path
                            data_category = personal_data_dict.get(data_type_lower)
                            DataCategory = data_category
                            DataType = data_type
                            InputText = data_type
                            KBIndex = rag.search_index(person_index, data_category)
                            if data_type not in data_category_dict:
                                data_category_dict[data_type] = rag.create_output_string(
                                    DataCategory, DataType, InputText, KBIndex
                                )
                        else:
                            # Not in dictionary - use LLM categorization
                            if data_type not in data_category_dict:
                                output = rag.retrieving(person_index, data_type, top_k=2)
                                print('--------Categorising data type...: ' + data_type)
                                num_tokens, llm_reply = agent.categorise_data_type(
                                    data_type, 
                                    text_segment, 
                                    output, 
                                    client,
                                    modelID='llama-3.3-70b-versatile'
                                )
                                data_category_dict[data_type] = llm_reply
                                time.sleep(5)

                        # Task 3: Categorize data collection party
                        num_tokens, llm_reply_party = agent.perform_categorisation_task(
                            text_segment, 
                            data_flow, 
                            party_responses, 
                            client, 
                            modelID='llama-3.1-8b-instant'
                        )
                        print('--------Processing data collection party for data flow: ' + str(data_flow))
                        time.sleep(5)

                        # Task 4: Categorize data collection purpose
                        num_tokens, llm_reply_purpose = agent.perform_categorisation_task(
                            text_segment, 
                            data_flow, 
                            collection_response, 
                            client, 
                            modelID='llama-3.1-8b-instant'
                        )
                        print('--------Processing data collection purpose for data flow: ' + str(data_flow))
                        time.sleep(5)

                        # Task 5: Categorize data collection method
                        num_tokens, llm_reply_method = agent.perform_categorisation_task(
                            text_segment, 
                            data_flow, 
                            method_responses, 
                            client, 
                            modelID='llama-3.1-8b-instant'
                        )
                        print('--------Processing data collection method for data flow: ' + str(data_flow))
                        time.sleep(5)
                        
                        # Write complete row to CSV
                        write_row([
                            str(idx), 
                            data_type, 
                            data_category_dict[data_type], 
                            json.dumps(data_flow), 
                            json.dumps(llm_reply_party), 
                            json.dumps(llm_reply_purpose), 
                            json.dumps(llm_reply_method)
                        ], 7)

                    time.sleep(10)  # Pause between segments
                    
            except Exception as e:
                print(f"Error processing segment with idx {idx}: {e}")

        client.close()


if __name__ == "__main__":
    # Example usage - process a privacy policy file
    input_file = 'data/vauxhall_clean.html'
    llm_pipeline(input_file)
