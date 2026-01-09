"""
Prompts Configuration for Privacy Policy Analysis

This module contains all LLM prompts used in the analysis pipeline.
Centralizing prompts here makes them easier to manage, version, and customize.

You can modify these prompts to:
- Adjust the analysis accuracy
- Change output formats
- Add new instructions
- Customize for different domains
"""


# ============================================================================
# DATA CATEGORIZATION PROMPTS
# ============================================================================

DATA_CATEGORIZATION_SYSTEM_PROMPT = """
1. You are an expert in categorise the INPUT DATA TYPE given by the user to extract key information about data collection/sharing.  
2. Please use the SENTENCE CONTEXT given by the user and the knowledge and your understanding of data types including its data category and data description provided in the list of CONTEXT given by the user to perform the categorisation.
3. Please strictly follow the below RULES when answering questions:
RULES: {answer_rules}
"""

DATA_CATEGORIZATION_ANSWER_RULES = """
Output has to follow the below JSON format. 
Only produce the answer in JSON format.
Make sure the produced output has valid JSON format
Don't include any other text in the answer such as input or query text
{{
  "Output": [
    {{
      "DataCategory": "data_category",
      "DataType": "data_type",
      "InputText": "input_text",
       "KBIndex" : "context_index"
    }}
  ]
}}
-data_category is the identified 'data category' defined in the CONTEXT, DO NOT create new data category
-data_type is the INPUT_DATA_TYPE
-input_text are the original text about INPUT_DATA_TYPE mentioned in the SENTENCE_CONTEXT
-context_index is the 'index id' the identified data category belong to, if you can't find one, output 'None'.
"""

DATA_CATEGORIZATION_USER_PROMPT = """
INPUT_DATA_TYPE: {data_type}
SENTENCE_CONTEXT: {query} 
CONTEXT: {context_1}
CONTEXT: {context_2}
"""


# ============================================================================
# DATA FLOW EXTRACTION PROMPTS
# ============================================================================

DATA_FLOW_EXTRACTION_SYSTEM_PROMPT = """
1. You are an expert to analyse the TEXT SEGMENT to (1) judge if it is about data collection and sharing (2) extract data flows
2. If the TEXT SEGMENT starts with '_table_', the paragraph content is separated using '|', and treat the first line of the paragraph as headings of different columns of the table and the second line of the paragraph as the table content.
2. Read and understand the TEXT SEGMENT and then strictly follow the below rules to produce your responses:
rules: {answer_rules} 
"""

DATA_FLOW_EXTRACTION_ANSWER_RULES = """ 
1. If the TEXT SEGMENT at least talk about one party collects data or personal information from another party, or a party shares data or personal information to another party
OUTPUT the extracted data flows in multiple JSON objects.
The JSON objects must use the format: 
{{
[
    {{
      "data_sender": "",
      "data_type": [],
      "data_receiver": []
    }}
]
}}
Each data flow represents one party (i.e., data_receiver) collects data (i.e., data_type) or personal information (i.e., data_type) from another party (i.e., data_sender), or a party shares (i.e., data_sender) data (i.e., data_type) or personal information (i.e., data_type) to another party (i.e., data_receiver)
    1.1 For data_types: you need to extract all atomic data/personal_information (i.e., data_type) following the below rules:
        1.1.1 When dealing with sentences that have combined data_types, I will split them into individual data_types for a clearer representation. 
        1.1.2 each data_type string MUST appear exactly as it does in the TEXT SEGMENT, do not change the cases 
        1.1.3 each data_type string MUST be explicitly mentioned in the given TEXT SEGMENT
        1.1.4 DO NOT INCLUDE any other text in the answer such as input or query text or your deduction or your explanation
        1.1.5 REMOVE Pronouns in the identified strings
        1.1.6 DO NOT INCLUDE strings that have specific addresses, postcodes, email addresses, companies, organisations, or geographical information. 
        1.1.7 if you can not identify a data_type, leave it empty
    1.2 For data_receivers and data_senders
        1.2.1  When dealing with sentences that have combined data_receivers or data_senders, I will split them into individual data_receiver or data_sender for a clearer representation. 
        1.2.2 each data_sender or data_receiver string MUST appear exactly as it does in the TEXT SEGMENT, do not change the cases 
        1.2.3 each data_sender or data_receiver string MUST be explicitly mentioned in the given TEXT SEGMENT
        1.2.4 if no data_sender is explicitly stated in the TEXT SEGMENT, leave data_sender empty. 
        1.2.5 if no data_receiver is explicitly stated in the TEXT SEGMENT, leave data_receiver empty. 
2. OUTPUT only 'NO' if the TEXT SEGMENT is about user's right about their data or personal information
3. OUTPUT only 'NO' for other cases/scenarios"""

DATA_FLOW_USER_PROMPT = """
TEXT SEGMENT: {query}
"""


# ============================================================================
# GENERAL CATEGORIZATION PROMPTS (Party, Purpose, Method)
# ============================================================================

GENERAL_CATEGORIZATION_SYSTEM_PROMPT = """
1. You are an expert in analysing text to perform a categorisation task for the input DATA_FLOW, given the context of TEXT SEGMENT and CONTEXT. 
2. The specifications of TEXT SEGMENT, DATA_FLOW, and CONTEXT are described as below:
    2.1 If the TEXT SEGMENT starts with '_table_', the paragraph content is separated using '|', and treat the first line of the paragraph as headings of different columns of the table and the second line of the paragraph as the table content.
    2.2 TEXT SEGMENT provides the text context for the DATA_FLOW
    2.3 DATA_FLOW is in JSON format, it describes a data flow that 'data_senders' share 'data_types' to 'data_receivers', or 'data_receivers' collects 'data_types' from 'data_senders'. The data flow is extracted from the TEXT SEGMENT
    2.4 A list of CONTEXT provides the domain knowledge of data collection and data sharing party including its category, detailed description, and some examples. 
3. Read and understand the user query and then strictly follow the below rules to produce your responses:
rules: {answer_rules} 
"""

GENERAL_CATEGORIZATION_ANSWER_RULES = """
Don't include any other text in the answer such as input or query text
Only produce ONE output for one DATA_FLOW using the JSON format below
{{
  "Output": [
    {{
      "DataCategory": "data_category",
      "InputText": "input_text",
      "KBIndex" : "context_index"
    }}
  ]
}}
-data_category is the identified 'data category' defined in the CONTEXT
-input_text are the original text sentence mentioned in the TEXT SEGMENT that is related to the data category,
-context_index is the 'index id' the identified data types belong to
"""

# User prompts with different numbers of contexts
GENERAL_CATEGORIZATION_USER_PROMPT_NO_CONTEXT = """
TEXT SEGMENT: {query}
DATA_FLOW: {data_flow}
CONTEXT: {context_1}
"""

GENERAL_CATEGORIZATION_USER_PROMPT_ONE_CONTEXT = """
TEXT SEGMENT: {query}
DATATYPE: {data_flow}
CONTEXT: {context}
"""

GENERAL_CATEGORIZATION_USER_PROMPT_TWO_CONTEXTS = """
TEXT SEGMENT: {query}
DATATYPE: {data_flow}
CONTEXT: {context_1}
CONTEXT: {context_2}
"""


# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================

# Default LLM model configurations
DEFAULT_MODELS = {
    'data_flow_extraction': 'llama-3.3-70b-versatile',
    'data_categorization': 'llama3-70b-8192',
    'general_categorization': 'llama-3.1-8b-instant'
}

# LLM generation parameters
LLM_PARAMETERS = {
    'temperature': 0.5,
    'top_p': 0.5,
    'max_tokens_categorization': 1024,
    'max_tokens_extraction': 2048,
    'stream': False
}

# Retrieval parameters
RETRIEVAL_PARAMETERS = {
    'similarity_threshold': 0.65,
    'top_k': 2
}


# ============================================================================
# HELPER FUNCTIONS FOR PROMPT CUSTOMIZATION
# ============================================================================

def get_prompt_template(prompt_name):
    """
    Get a prompt template by name.
    
    Args:
        prompt_name (str): Name of the prompt template
        
    Returns:
        str: The prompt template
        
    Raises:
        ValueError: If prompt_name is not found
    """
    prompts = {
        'data_categorization_system': DATA_CATEGORIZATION_SYSTEM_PROMPT,
        'data_categorization_rules': DATA_CATEGORIZATION_ANSWER_RULES,
        'data_categorization_user': DATA_CATEGORIZATION_USER_PROMPT,
        'data_flow_system': DATA_FLOW_EXTRACTION_SYSTEM_PROMPT,
        'data_flow_rules': DATA_FLOW_EXTRACTION_ANSWER_RULES,
        'data_flow_user': DATA_FLOW_USER_PROMPT,
        'general_categorization_system': GENERAL_CATEGORIZATION_SYSTEM_PROMPT,
        'general_categorization_rules': GENERAL_CATEGORIZATION_ANSWER_RULES,
        'general_categorization_user_no_context': GENERAL_CATEGORIZATION_USER_PROMPT_NO_CONTEXT,
        'general_categorization_user_one_context': GENERAL_CATEGORIZATION_USER_PROMPT_ONE_CONTEXT,
        'general_categorization_user_two_contexts': GENERAL_CATEGORIZATION_USER_PROMPT_TWO_CONTEXTS,
    }
    
    if prompt_name not in prompts:
        raise ValueError(f"Prompt '{prompt_name}' not found. Available prompts: {list(prompts.keys())}")
    
    return prompts[prompt_name]


def customize_prompt(prompt_name, modifications):
    """
    Customize a prompt template with modifications.
    
    Args:
        prompt_name (str): Name of the prompt to customize
        modifications (dict): Dictionary of string replacements
        
    Returns:
        str: Modified prompt template
        
    Example:
        >>> mods = {'JSON format': 'YAML format', 'expert': 'specialist'}
        >>> new_prompt = customize_prompt('data_categorization_system', mods)
    """
    prompt = get_prompt_template(prompt_name)
    for old_text, new_text in modifications.items():
        prompt = prompt.replace(old_text, new_text)
    return prompt


def get_model_config(task_type='general_categorization'):
    """
    Get the default model configuration for a task type.
    
    Args:
        task_type (str): Type of task ('data_flow_extraction', 'data_categorization', 
                         or 'general_categorization')
        
    Returns:
        str: Model ID for the task
    """
    return DEFAULT_MODELS.get(task_type, DEFAULT_MODELS['general_categorization'])


def get_llm_parameters(task_type='categorization'):
    """
    Get LLM generation parameters for a task type.
    
    Args:
        task_type (str): Either 'categorization' or 'extraction'
        
    Returns:
        dict: LLM parameters
    """
    params = LLM_PARAMETERS.copy()
    if task_type == 'extraction':
        params['max_tokens'] = params['max_tokens_extraction']
    else:
        params['max_tokens'] = params['max_tokens_categorization']
    return params
