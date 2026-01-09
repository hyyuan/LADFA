"""
Groq API Client Initialization Module

This module provides utilities to initialize and configure the Groq API client
by reading the API key from a file.
"""

from groq import Groq


def getAPIkey(file_path):
    """
    Read the API key from a file.
    
    Args:
        file_path (str): Path to the file containing the API key
        
    Returns:
        str: The API key string
    """
    with open(file_path, 'r') as file:
        api_key = file.read().strip()
    return api_key


def getGroqClient(api_key_path):
    """
    Initialize and return a Groq client with the API key from the specified file.
    
    Args:
        api_key_path (str): Path to the file containing the Groq API key
        
    Returns:
        Groq: Initialized Groq client instance
    """
    client = Groq(
        api_key=getAPIkey(api_key_path),
    )
    return client
