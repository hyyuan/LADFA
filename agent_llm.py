"""
LLM Agent Module for Privacy Policy Analysis

This module provides LLM-based agents for analyzing privacy policy text,
extracting data flows, and categorizing data collection practices. It uses
Groq's API to interact with various LLM models.

Note: All prompts have been moved to prompts_config.py for easier management.
"""

try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel

from typing import List, Optional
import json

# Import prompts configuration
try:
    import prompts_config as prompts
except ImportError:
    import cleaned_framework.prompts_config as prompts


class DataFlow(BaseModel):
    """Model representing a data flow between sender and receiver."""
    data_sender: str
    data_type: str
    data_receiver: str


def compose_data_type_context(retriever_response):
    """
    Create formatted context string from retriever response.
    
    Args:
        retriever_response: Response object from vector index retrieval
        
    Returns:
        str: Formatted context string with index ID, category, and description
    """
    data_context = (
        "Index ID: " + retriever_response.node_id + "\n" + 
        "Data category: " + retriever_response.metadata['name'] + "\n" + 
        "Data description: " + retriever_response.text
    )
    return data_context


def get_system_prompt(prompt):
    """
    Create a system prompt message for the LLM.
    
    Args:
        prompt (str): The system prompt content
        
    Returns:
        dict: Formatted system message
    """
    system_prompt = {
        "role": "system",
        "content": prompt
    }
    return system_prompt


def get_user_prompt_text_(query):
    """
    Create a user prompt from query text.
    
    Args:
        query (str): The user query text
        
    Returns:
        str: Formatted user prompt
    """
    return prompts.DATA_FLOW_USER_PROMPT.format(query=query)


def create_system_prompt_data_categorise(answer_rules):
    """
    Create system prompt for data categorization task.
    
    Args:
        answer_rules (str): Rules defining how the LLM should respond
        
    Returns:
        str: Formatted system prompt
    """
    return prompts.DATA_CATEGORIZATION_SYSTEM_PROMPT.format(answer_rules=answer_rules)


def set_anwser_rule_data_categorise():
    """
    Define answer rules for data categorization task.
    
    Returns:
        str: JSON format rules for LLM output
    """
    return prompts.DATA_CATEGORIZATION_ANSWER_RULES


def create_user_prompt_data_categorise(data_type, query, context_1, context_2):
    """
    Create user prompt for data categorization with context.
    
    Args:
        data_type (str): The data type to categorize
        query (str): The sentence context
        context_1 (str): First context from knowledge base
        context_2 (str): Second context from knowledge base
        
    Returns:
        str: Formatted user prompt
    """
    return prompts.DATA_CATEGORIZATION_USER_PROMPT.format(
        data_type=data_type,
        query=query,
        context_1=context_1,
        context_2=context_2
    )


def categorise_data_type(data_type, query, retrieving_response, client, modelID="llama3-8b-8192"):
    """
    Categorize a data type using LLM with retrieved context.
    
    Args:
        data_type (str): The data type to categorize
        query (str): The sentence containing the data type
        retrieving_response (list): Retrieved context from knowledge base
        client: Groq API client
        modelID (str): LLM model identifier
        
    Returns:
        tuple: (num_tokens, llm_reply) - Token count and LLM response
    """
    # Prepare context from top 2 retrieval results
    context_1 = compose_data_type_context(retrieving_response[0])
    context_2 = compose_data_type_context(retrieving_response[1])

    messages = [
        get_system_prompt(create_system_prompt_data_categorise(set_anwser_rule_data_categorise())),
        {
            "role": "user",
            "content": create_user_prompt_data_categorise(data_type, query, context_1, context_2)
        }
    ]

    # Call Groq API
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=modelID,
        temperature=0.5,
        max_tokens=1024,
        top_p=0.5,
        stream=False
    )

    # Extract response and token usage
    llm_reply = chat_completion.choices[0].message.content
    num_token = chat_completion.usage.total_tokens

    return num_token, llm_reply


def create_selecting_paragraph_get_data_flows_system_prompt(answer_rules):
    """
    Create system prompt for paragraph selection and data flow extraction.
    
    Args:
        answer_rules (str): Rules for how to identify and extract data flows
        
    Returns:
        str: Formatted system prompt
    """
    return prompts.DATA_FLOW_EXTRACTION_SYSTEM_PROMPT.format(answer_rules=answer_rules)


def set_selecting_paragraph_get_data_flows_answer_rules():
    """
    Define rules for extracting data flows from paragraphs.
    
    Returns:
        str: Detailed rules for data flow extraction
    """
    return prompts.DATA_FLOW_EXTRACTION_ANSWER_RULES


def selecting_paragraph_get_data_flows(client, segmented_text, modelID="llama-3.1-70b-versatile"):
    """
    Analyze a text segment to identify if it contains data flows and extract them.
    
    Args:
        client: Groq API client
        segmented_text (str): Text segment to analyze
        modelID (str): LLM model identifier
        
    Returns:
        tuple: (num_tokens, llm_reply) - Token count and LLM response (JSON or 'NO')
    """
    system_prompt = create_selecting_paragraph_get_data_flows_system_prompt(
        answer_rules=set_selecting_paragraph_get_data_flows_answer_rules()
    )
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": get_user_prompt_text_(segmented_text)
            }
        ],
        model=modelID,
        temperature=0.5,
        max_tokens=2048,
        top_p=0.5,
        stream=False
    )

    llm_reply = chat_completion.choices[0].message.content
    num_token = chat_completion.usage.total_tokens
    return num_token, llm_reply


def create_system_prompt_categorisation_task(answer_rules):
    """
    Create system prompt for categorization tasks (party, purpose, method).
    
    Args:
        answer_rules (str): Rules defining the categorization task
        
    Returns:
        str: Formatted system prompt
    """
    return prompts.GENERAL_CATEGORIZATION_SYSTEM_PROMPT.format(answer_rules=answer_rules)


def set_anwser_rule_categorisation_task():
    """
    Define answer rules for categorization tasks.
    
    Returns:
        str: JSON format rules for categorization output
    """
    return prompts.GENERAL_CATEGORIZATION_ANSWER_RULES


def create_user_prompt_categorisation_task(query, responses, data_flow, response_threshold=0.6):
    """
    Create user prompt for categorization task with dynamic context selection.
    
    Selects relevant context based on similarity threshold and formats prompt accordingly.
    
    Args:
        query (str): TEXT SEGMENT text
        responses (list): Retrieved context responses
        data_flow (str): Data flow JSON string
        response_threshold (float): Similarity threshold for context selection
        
    Returns:
        str: Formatted user prompt with query, data flow, and context
    """
    # Filter contexts by similarity threshold
    context_arr = []
    for response in responses:
        if response.get_score() >= response_threshold:
            context_arr.append(compose_data_type_context(response))

    # Create prompt based on number of relevant contexts found
    if len(context_arr) == 0:
        # No high-scoring contexts, use top result
        context_1 = compose_data_type_context(responses[0])
        return prompts.GENERAL_CATEGORIZATION_USER_PROMPT_NO_CONTEXT.format(
            query=query,
            data_flow=data_flow,
            context_1=context_1
        )

    elif len(context_arr) == 1:
        # One relevant context
        context = context_arr[0]
        return prompts.GENERAL_CATEGORIZATION_USER_PROMPT_ONE_CONTEXT.format(
            query=query,
            data_flow=data_flow,
            context=context
        )

    else:
        # Multiple relevant contexts, use top 2
        context_1 = context_arr[0]
        context_2 = context_arr[1]
        return prompts.GENERAL_CATEGORIZATION_USER_PROMPT_TWO_CONTEXTS.format(
            query=query,
            data_flow=data_flow,
            context_1=context_1,
            context_2=context_2
        )


def perform_categorisation_task(query, data_flow, retrieving_response, client, modelID="llama-3.1-70b-versatile"):
    """
    Perform categorization task for data collection party, purpose, or method.
    
    Args:
        query (str): TEXT SEGMENT text
        data_flow (str): Data flow JSON string
        retrieving_response (list): Retrieved context from knowledge base
        client: Groq API client
        modelID (str): LLM model identifier
        
    Returns:
        tuple: (num_tokens, llm_reply) - Token count and LLM response
    """
    messages = [
        get_system_prompt(create_system_prompt_categorisation_task(set_anwser_rule_categorisation_task())),
        {
            "role": "user",
            "content": create_user_prompt_categorisation_task(query, retrieving_response, data_flow, 0.65)
        }
    ]

    # Call Groq API
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=modelID,
        temperature=0.5,
        max_tokens=2048,
        top_p=0.5,
        stream=False
    )

    # Extract response and token usage
    llm_reply = chat_completion.choices[0].message.content
    num_token = chat_completion.usage.total_tokens

    return num_token, llm_reply
