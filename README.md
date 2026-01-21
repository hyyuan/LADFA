# LADFA: A Framework using (L)LMs and R(A)G for Personal (D)ata (F)low (A)nalysis in Privacy Policies

[![Paper](https://img.shields.io/badge/arXiv-2601.10413-b31b1b.svg)](https://arxiv.org/abs/2601.10413)

An automated framework for analyzing privacy policies using Large Language Models (LLMs) and Retrieval Augmented Generation (RAG). This system extracts data flows from privacy policies, categorizes data types, identifies collection parties, and analyzes purposes and methods of data processing.

**Paper**: [LADFA: A Framework of Using Large Language Models and Retrieval-Augmented Generation for Personal Data Flow Analysis in Privacy Policies](https://arxiv.org/abs/2601.10413)

## 📋 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Installation](#-installation)
3. [Setup](#-setup)
4. [Quick Start](#-quick-start)
5. [File Structure](#-file-structure)
6. [Workflow](#-workflow)
7. [Output Files](#-output-files)
8. [Troubleshooting](#-troubleshooting)
9. [Citation](#-citation)

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
- HTML network visualizations
- Network metrics (centrality, paths, degrees)
- Statistical analysis files
   - `results/example_policy_verification.csv` - Random verification samples
   - `results/example_policy_metrics.csv` - Network metrics summary
   - `results/example_policy_basics.csv` - Basic graph statistics
   - `results/example_policy_between.csv` - Betweenness centrality
   - `results/example_policy_close.csv` - Closeness centrality
   - `results/example_policy_central.csv` - Degree centrality
   - `results/example_policy_tree.csv` - Spanning tree analysis
   - `results/example_policy_longest_path.csv` - Longest paths in graph
   - `results/example_policy.html` - HTML graph visualizations

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

For advanced configuration options including batch processing, custom LLM models, prompt customization, and RAG parameter tuning, see [ADVANCED_USAGE.md](ADVANCED_USAGE.md).

## 📄 Citation

If you use LADFA in your research, please cite our paper:

```bibtex
@misc{yuan2026,
      title={LADFA: A Framework of Using Large Language Models and Retrieval-Augmented Generation for Personal Data Flow Analysis in Privacy Policies}, 
      author={Haiyue Yuan and Nikolay Matyunin and Ali Raza and Shujun Li},
      year={2026},
      eprint={2601.10413},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2601.10413}, 
}
```
