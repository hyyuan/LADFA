# LADFA: A Framework using (L)LMs and R(A)G for Personal (D)ata (F)low (A)nalysis in Privacy Policies

An automated framework for analyzing privacy policies using Large Language Models (LLMs) and Retrieval Augmented Generation (RAG). This system extracts data flows from privacy policies, categorizes data types, identifies collection parties, and analyzes purposes and methods of data processing.

## 📋 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Installation](#-installation)
3. [Setup](#-setup)
4. [Quick Start](#-quick-start)
5. [File Structure](#-file-structure)
6. [Workflow](#-workflow)
7. [Output Files](#-output-files)
8. [Troubleshooting](#-troubleshooting)

## ✅ Prerequisites

### System Requirements
- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended)
- Internet connection for LLM API calls

### Required Accounts
- **Groq API Account** - Sign up at [console.groq.com](https://console.groq.com)
  - Get your API key from the dashboard
  - Free tier available with rate limits

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

## ⚙️ Setup

### Step 1: Configure API Key

Create a file named `GROQ_API_KEY` in this directory:

```bash
echo "your_actual_api_key_here" > GROQ_API_KEY
```

**Important**: This file is in `.gitignore` and will never be committed to the repository.

### Step 2: Prepare Knowledge Bases

Ensure the `kb/` directory contains these JSON files:
- `data_categories_kt.json` - Personal data type categories
- `data_consumer_type_kt.json` - Data collection party types
- `data_processing_purpose_kt.json` - Data processing purposes
- `data_processing_method_kt.json` - Data collection/processing methods

### Step 3: Add Privacy Policy Files

Place your privacy policy files in the `data/` directory:
- Supported formats: `.html`, `.htm`, `.pdf`

```bash
cp /path/to/your/policy.html data/
```

### Step 4: Verify Setup

Check that everything is configured correctly:

```bash
python check_setup.py
```

This will verify:
- API key file exists
- Knowledge base files are present
- Required Python packages are installed
- Privacy policy files are available

## 🚀 Quick Start

### Step 1: Verify Prerequisites

```bash
python check_setup.py
```

### Step 2: Analyze a Privacy Policy

```python
import main_pipeline

# Analyze HTML or PDF file
main_pipeline.llm_pipeline('data/example_policy.html')
```

This will:
- Extract and segment text from the policy
- Identify data flows using LLM analysis
- Categorize data types, parties, purposes, and methods
- Generate CSV files with results:
  - `data/example_policy_segment.csv` - Text segments
  - `data/example_policy_output.csv` - Complete analysis results

### Step 3: Generate Visualizations

```python
import main_pipeline_visualisation

# Generate network graphs and metrics
# Parameters: (policy_name, main_party_name)
main_pipeline_visualisation.run('example_policy', 'CompanyName')
```

This will generate:
- Interactive HTML network visualizations
- Network metrics (centrality, paths, degrees)
- Statistical analysis files

All outputs are saved to the same directory as the input file.

## 📁 File Structure

### Core Pipeline Scripts

1. **`main_pipeline.py`** - Main analysis pipeline
   - Processes HTML/PDF privacy policies
   - Extracts data flows using LLM analysis
   - Categorizes data types, parties, purposes, and methods
   - Outputs structured CSV results

2. **`main_pipeline_visualisation.py`** - Visualization pipeline
   - Generates network graphs from analysis results
   - Produces statistical metrics
   - Creates interactive HTML visualizations

### Supporting Modules

3. **`groq_client.py`** - Groq API client initialization
   - Reads API key from file
   - Initializes Groq client for LLM interactions

4. **`html2text.py`** - HTML parsing and text extraction
   - Extracts text from HTML privacy policies
   - Handles headers, paragraphs, lists, and tables
   - Segments text for processing

5. **`pdf2text.py`** - PDF text extraction
   - Extracts and chunks PDF content
   - Splits based on numbered headings and paragraphs

6. **`rag.py`** - Retrieval Augmented Generation
   - Converts JSON knowledge bases to vector indexes
   - Performs similarity search for categorization
   - Uses HuggingFace embeddings (BAAI/bge-small-en-v1.5)

7. **`agent_llm.py`** - LLM agent operations
   - Creates prompts for various analysis tasks
   - Handles data flow extraction
   - Performs categorization tasks (data types, parties, purposes, methods)

8. **`post_processor.py`** - Post-processing and network analysis
   - Constructs data flow graphs from CSV results
   - Calculates network metrics (centrality, paths, trees)
   - Generates interactive Pyvis visualizations
   - Handles entity normalization and abbreviations

9. **`check_setup.py`** - Prerequisites verification
   - Verifies API key, knowledge bases, and dependencies
   - Run before analyzing policies

10. **`prompts_config.py`** - Prompt templates and LLM configuration
    - Centralized prompt management for all LLM tasks
    - Default model configurations for different tasks
    - LLM generation parameters (temperature, tokens, etc.)
    - Helper functions for prompt customization

## 🔄 Workflow

### Analysis Pipeline (main_pipeline.py)
```
Privacy Policy (HTML/PDF)
    ↓
Text Extraction & Segmentation
    ↓
Data Flow Identification (LLM)
    ↓
Categorization using RAG
    ↓
CSV Results (*_output.csv)
```

### Visualization Pipeline (main_pipeline_visualisation.py)
```
CSV Results
    ↓
Graph Construction
    ↓
Network Analysis & Metrics
    ↓
Interactive HTML Visualizations
```

## 📊 Output Files

### From main_pipeline.py
- `*_segment.csv` - Text segments extracted from input
- `*_output.csv` - Complete analysis results with data flows and categorizations

### From main_pipeline_visualisation.py
- `*_verification.csv` - Random verification samples
- `*_metrics.csv` - Network metrics summary
- `*_basics.csv` - Basic graph statistics
- `*_between.csv` - Betweenness centrality
- `*_close.csv` - Closeness centrality
- `*_central.csv` - Degree centrality
- `*_tree.csv` - Spanning tree analysis
- `*_longest_path.csv` - Longest paths in graph
- Interactive HTML graph visualizations

## 🔧 Troubleshooting

### API Key Issues
- Ensure `GROQ_API_KEY` file exists in the project directory
- File should contain only your API key (no quotes or extra text)
- Verify key is valid at [console.groq.com](https://console.groq.com)

### Missing Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Knowledge Base Errors
- Verify all 4 JSON files exist in `kb/` directory
- Check JSON files are properly formatted
- Ensure files match expected schema

### Rate Limiting
- The framework includes automatic delays to respect API rate limits
- If you encounter rate limit errors, the delays may need adjustment
- Free tier has lower rate limits than paid tiers

### Memory Issues
- Large policies may require 16GB+ RAM
- Process policies in smaller chunks if needed
- Close other applications to free memory

## 📚 Dependencies

### Core Libraries
- `groq` - Groq API client for LLM operations
- `llama_index` - Vector indexing and retrieval for RAG
- `beautifulsoup4`, `lxml` - HTML parsing
- `pypdf` - PDF text extraction
- `networkx` - Graph construction and analysis
- `pyvis` - Interactive network visualizations
- `spacy` - Natural language processing
- `pandas`, `numpy` - Data manipulation

See [`requirements.txt`](requirements.txt) for complete list.

## 🛠️ Advanced Usage

### Batch Processing

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

### Custom API Key Location

```python
import groq_client

client = groq_client.getGroqClient('/custom/path/to/api_key')
```

### Customising Prompts

The framework uses `prompts_config.py` to manage all LLM prompts. You can customise prompts for different use cases

### Adjusting LLM Configuration

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

**Available LLM Models** (configure in `prompts_config.DEFAULT_MODELS`):
- `llama-3.3-70b-versatile` - Data flow extraction (default)
- `llama3-70b-8192` - Data type categorization (default)
- `llama-3.1-8b-instant` - Party/purpose/method categorization (default)

**LLM Parameters** (configure in `prompts_config.LLM_PARAMETERS`):
- `temperature`: 0.5 (creativity vs. consistency)
- `top_p`: 0.5 (nucleus sampling)
- `max_tokens_categorization`: 1024
- `max_tokens_extraction`: 2048
- `stream`: False

**To modify configurations**, edit `prompts_config.py`:


### Using Custom LLM in agent_llm.py

When calling agent functions, you can override default models:

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

### Adjusting RAG Retrieval Parameters

Configure retrieval parameters in `prompts_config.py`:

```python
# In prompts_config.py
RETRIEVAL_PARAMETERS = {
    'similarity_threshold': 0.65,  # Minimum similarity score
    'top_k': 2                      # Number of results to retrieve
}
```

## 📧 Support

For issues or questions:
- Check module docstrings for detailed function documentation
- Review error messages and stack traces
- Ensure all prerequisites are met using `check_setup.py`

## 📄 License

See project documentation for license information.
