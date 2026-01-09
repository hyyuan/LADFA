"""
RAG (Retrieval Augmented Generation) Module

This module provides functionality for building and querying vector indexes using LlamaIndex
for knowledge base operations. It supports document conversion, indexing with HuggingFace
embeddings, and retrieval operations.
"""

import json
import os
from llama_index.core import Document, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core.retrievers import VectorIndexRetriever


def convert_json(json_file_path):
    """
    Convert JSON knowledge base data to LlamaIndex Document objects.
    
    Args:
        json_file_path (str): Path to the JSON file containing data types
        
    Returns:
        list: List of Document objects with text and metadata
    """
    # Load JSON data from file
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)

    # Convert each DataType entry to a Document object
    # Combines description and items into text, stores name as metadata
    documents = [
        Document(
            text=doc['description'] + ' ' + ', '.join(doc.get('items', [])), 
            metadata={'name': doc['name']}
        ) 
        for doc in json_data['DataTypes']
    ]
    return documents


def indexingHuggingfaceEmbedding(documents, save_dir, embed_model_name="BAAI/bge-small-en-v1.5"):
    """
    Create or load a vector index using HuggingFace embeddings.
    
    If the index directory doesn't exist, creates a new index from documents.
    Otherwise, loads the existing index from storage.
    
    Args:
        documents (list): List of Document objects to index
        save_dir (str): Directory to save/load the index
        embed_model_name (str): HuggingFace model name for embeddings
        
    Returns:
        VectorStoreIndex: The created or loaded vector index
    """
    # Configure the embedding model
    Settings.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
    
    if not os.path.exists(save_dir):
        # Create new index if directory doesn't exist
        os.makedirs(save_dir)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=save_dir)
    else:
        # Load existing index from storage
        index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=save_dir),
        )
    return index


def retrieving(index, query, top_k=3):
    """
    Retrieve the top-k most similar documents for a given query.
    
    Args:
        index (VectorStoreIndex): The vector index to query
        query (str): The query text
        top_k (int): Number of top results to return
        
    Returns:
        list: List of retrieved nodes with similarity scores
    """
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=top_k,
    )
    return retriever.retrieve(query)


def search_index(index, category):
    """
    Search the index for a specific category and return its node IDs.
    
    Args:
        index (VectorStoreIndex): The vector index to search
        category (str): The category name to search for
        
    Returns:
        list or None: List of node IDs associated with the category, or None if not found
    """
    tmp_dict = index.ref_doc_info
    keys = tmp_dict.keys()
    for key in keys:
        tmp_value = tmp_dict.get(key)
        if category == tmp_value.metadata.get('name'):
            node_id = tmp_value.node_ids
            return node_id


def json_to_dict(json_file_path):
    """
    Convert JSON knowledge base to a dictionary mapping items to their category names.
    
    Args:
        json_file_path (str): Path to the JSON file
        
    Returns:
        dict: Dictionary mapping lowercase items to their category names
    """
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Initialize dictionary for transformation
    transformed_data = {}

    # Iterate through DataTypes and map each item to its category name
    for data_type in data["DataTypes"]:
        name = data_type["name"]  # Category name
        items = data_type["items"]  # List of items in this category

        # Add each item to the dictionary (lowercase for matching)
        for item in items:
            item = item.lower()
            transformed_data[item] = name
            
    return transformed_data


def create_output_string(DataCategory, DataType, InputText, KBIndex):
    """
    Create a formatted JSON output string for categorization results.
    
    Args:
        DataCategory (str): The identified data category
        DataType (str): The data type being categorized
        InputText (str): The original input text
        KBIndex (str): The knowledge base index ID
        
    Returns:
        str: JSON formatted string with the output structure
    """
    # Create output structure as dictionary
    output_data = {
        "Output": [
            {
                "DataCategory": DataCategory,
                "DataType": DataType,
                "InputText": InputText,
                "KBIndex": KBIndex
            }
        ]
    }

    # Convert to JSON string with formatting
    json_output = json.dumps(output_data, indent=4)
    return json_output
