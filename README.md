# LADFA: A Framework using (L)LMs and R(A)G for Personal (D)ata (F)low (A)nalysis in Privacy Policies

This folder contains the cleaned and documented version of the privacy policy analysis framework. All unused scripts have been removed, and remaining scripts have been thoroughly commented for better understanding and maintainability.

## 🚀 Quick Start for New Users

**New to this framework?** Start here:

1. **Read First**: [`GETTING_STARTED.md`](GETTING_STARTED.md) - Complete setup guide
2. **Run Example**: `python example_usage.py` - Interactive tutorial
3. **Quick Reference**: [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - Command cheatsheet

## 📁 Directory Contents

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

## 🔄 Workflow

### Analysis Pipeline
```
Privacy Policy (HTML/PDF)
    ↓
Text Extraction (html2text.py / pdf2text.py)
    ↓
Text Segmentation
    ↓
Data Flow Extraction (agent_llm.py + Groq API)
    ↓
Categorization using RAG (rag.py + agent_llm.py)
    ↓
CSV Results
```

### Visualization Pipeline
```
CSV Results
    ↓
Graph Construction (post_processor.py)
    ↓
Network Analysis
    ↓
Interactive HTML Visualizations
```

## 📦 Dependencies

See [`requirements.txt`](requirements.txt) for complete list.

**Quick Install**:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Key Libraries
- `groq` - Groq API client
- `llama_index` - Vector indexing and retrieval
- `beautifulsoup4` - HTML parsing
- `pypdf` - PDF text extraction
- `networkx` - Graph analysis
- `pyvis` - Network visualization
- `spacy` - Natural language processing

### Knowledge Bases Required
The scripts expect the following knowledge typologies files in `kb/`:
- `data_categories_kt.json` - Personal data categories
- `data_consumer_type_kt.json` - Data consumer types
- `data_processing_purpose_kt.json` - Data processing purposes
- `data_processing_method_kt.json` - Data processing methods

### External Resources
- Groq API key (stored in `GROQ_API_KEY` file in parent directory)
- spaCy model: `en_core_web_sm`

## 🚀 Usage

### Option 1: Interactive Example Script (Recommended)
```bash
python example_usage.py
```

This launches an interactive menu to:
- Check prerequisites
- Analyze single or multiple policies
- Generate visualizations
- Run complete workflows

### Option 2: Direct Python Import

**Running the Analysis Pipeline**:
```python
from cleaned_framework import main_pipeline

# Process a privacy policy (HTML or PDF)
input_file = 'data/example_clean.html'
main_pipeline.llm_pipeline(input_file)
```

**Running the Visualization Pipeline**:
```python
from cleaned_framework import main_pipeline_visualisation

# Generate visualizations for a processed policy
# First parameter: policy name
# Second parameter: main party/company name
main_pipeline_visualisation.run('example', 'example_party')
```

### Option 3: Batch Processing

See [`example_usage.py`](example_usage.py) for batch processing examples.

## 📚 Documentation Files

- **[`GETTING_STARTED.md`](GETTING_STARTED.md)** - Complete setup and installation guide
- **[`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)** - Quick command reference
- **[`example_usage.py`](example_usage.py)** - Interactive examples and tutorials
- **[`config.template.json`](config.template.json)** - Configuration reference


The pipeline generates several types of outputs:

### From main_pipeline.py
- `*_segment.csv` - Text segments extracted from input
- `*_output.csv` - Complete analysis results

### From main_pipeline_visualisation.py
- `*_verification.csv` - Verification samples
- `*_metrics.csv` - Network metrics
- `*_basics.csv` - Basic statistics
- `*_between.csv` - Betweenness centrality
- `*_close.csv` - Closeness centrality
- `*_central.csv` - Degree centrality
- `*_tree.csv` - Tree structures
- `*_longest_path.csv` - Longest paths
- Interactive HTML graph visualizations

## 🛠️ Important Notes

- The framework uses rate limiting (sleep delays) to respect API limits
- Vector indexes are cached in directories to avoid recomputation
- spaCy model must be downloaded: `python -m spacy download en_core_web_sm`
- Groq API key must be stored in the parent directory

## 📧 Support

For issues or questions about this cleaned framework, refer to the individual module docstrings or the original project documentation.
