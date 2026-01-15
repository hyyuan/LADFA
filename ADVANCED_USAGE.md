# Advanced Usage Guide

This guide covers advanced configuration and customization options for the LADFA framework.

## Batch Processing

Process multiple privacy policies in sequence:

```python
import main_pipeline

policies = [
    'data/policy1.html',
    'data/policy2.pdf',
    'data/policy3.html'
]

for policy in policies:
    main_pipeline.llm_pipeline(policy)
```

## Custom API Key Location

Specify a custom path for your API key file:

```python
import groq_client

client = groq_client.getGroqClient('/custom/path/to/api_key')
```

## Customizing Prompts

The framework uses `prompts_config.py` to manage all LLM prompts. You can customize prompts for different use cases by modifying this file.

## Adjusting LLM Configuration

Configure LLM models and parameters in `prompts_config.py`:

```python
import prompts_config as prompts

# Get default model for a task
model_id = prompts.get_model_config('data_flow_extraction')
# Returns: 'llama-3.3-70b-versatile'

# Get LLM parameters
params = prompts.get_llm_parameters('extraction')
# Returns: {'temperature': 0.5, 'top_p': 0.5, 'max_tokens': 2048, 'stream': False}
```

### Used LLM Models

Configure in `prompts_config.DEFAULT_MODELS`:
- `llama-3.3-70b-versatile` - Data flow extraction (default)
- `llama3-70b-8192` - Data type categorization (default)
- `llama-3.1-8b-instant` - Party/purpose/method categorization (default)

### LLM Parameters

Configure in `prompts_config.LLM_PARAMETERS`:
- `temperature`: 0.5 (creativity vs. consistency)
- `top_p`: 0.5 (nucleus sampling)
- `max_tokens_categorization`: 1024
- `max_tokens_extraction`: 2048
- `stream`: False

## Using Custom LLM Models

Override default models when calling agent functions:

```python
import agent_llm as agent
import groq_client

client = groq_client.getGroqClient('GROQ_API_KEY')

# Data flow extraction with custom model
num_tokens, data_flows = agent.selecting_paragraph_get_data_flows(
    client, 
    text_segment, 
    modelID="llama-3.3-70b-versatile"  # Specify model
)

# Data categorization with custom model
num_tokens, llm_reply = agent.categorise_data_type(
    data_type,
    text_segment,
    output,
    client,
    modelID='llama3-70b-8192'  # Specify model
)

# General categorization (party/purpose/method)
num_tokens, llm_reply = agent.perform_categorisation_task(
    text_segment,
    data_flow,
    context,
    client,
    modelID='llama-3.1-8b-instant'  # Specify model
)
```

## Adjusting RAG Retrieval Parameters

Configure retrieval parameters in `prompts_config.py`:

```python
# In prompts_config.py
RETRIEVAL_PARAMETERS = {
    'similarity_threshold': 0.65,  # Minimum similarity score
    'top_k': 2                      # Number of results to retrieve
}
```

Adjust these parameters to fine-tune the balance between precision and recall in knowledge base retrieval.
