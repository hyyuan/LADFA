# Quick Reference Guide - Cleaned Framework

## 🚀 Quick Start

### 1. Analyze a Privacy Policy
```python
from cleaned_framework import main_pipeline

# Process HTML file
main_pipeline.llm_pipeline('data/example_policy.html')

# Process PDF file  
main_pipeline.llm_pipeline('data/example_policy.pdf')
```

### 2. Generate Visualizations
```python
from cleaned_framework import main_pipeline_visualisation

# Generate all visualizations and metrics
main_pipeline_visualisation.run('example', 'example_company')
```

## 📚 Module Reference

### groq_client.py
```python
from cleaned_framework import groq_client

# Initialize Groq client
client = groq_client.getGroqClient('path/to/api_key.txt')
```

### html2text.py
```python
from cleaned_framework import html2text

# Extract text segments from HTML
segments = html2text.extract_and_process_text_from_file('policy.html')
```

### pdf2text.py
```python
from cleaned_framework import pdf2text

# Extract text chunks from PDF
chunks = pdf2text.split_pdf('policy.pdf')
```

### rag.py
```python
from cleaned_framework import rag

# Convert JSON to documents
docs = rag.convert_json('kb/data_types.json')

# Create/load index
index = rag.indexingHuggingfaceEmbedding(docs, 'index_dir/')

# Retrieve similar documents
results = rag.retrieving(index, "personal information", top_k=3)

# Convert JSON to dictionary
data_dict = rag.json_to_dict('kb/data_types.json')
```

### agent_llm.py
```python
from cleaned_framework import agent_llm

# Extract data flows from text
num_tokens, flows_json = agent_llm.selecting_paragraph_get_data_flows(
    client, 
    text_segment, 
    modelID="llama-3.3-70b-versatile"
)

# Categorize data type
num_tokens, category = agent_llm.categorise_data_type(
    data_type, 
    context_text, 
    retrieval_results, 
    client
)

# Perform categorization task (party/purpose/method)
num_tokens, result = agent_llm.perform_categorisation_task(
    text, 
    data_flow, 
    retrieval_results, 
    client
)
```

### post_processor.py
```python
from cleaned_framework import post_processor

# Full post-processing with verification
processor.post_processing(
    input_csv='results/data.csv',
    main_party='company_name',
    segment_csv='results/segments.csv',
    option='betweenness',
    top_n=10,
    verification_csv='results/verify.csv',
    metrics_csv='results/metrics.csv',
    basics_csv='results/basics.csv'
)

# Simple post-processing with multiple metrics
processor.post_processing_simple(
    input_csv='results/data.csv',
    main_party='company_name',
    segment_csv='results/segments.csv',
    top_n=10,
    between_csv='results/betweenness.csv',
    close_csv='results/closeness.csv',
    central_csv='results/centrality.csv',
    tree_csv='results/tree.csv',
    longest_path_csv='results/path.csv',
    longest_path_length_csv='results/path_len.csv',
    most_inwards_csv='results/inward.csv',
    most_outwards_csv='results/outward.csv'
)
```

## 🔧 Common Workflows

### Complete Analysis Pipeline
```python
from cleaned_framework import main_pipeline, main_pipeline_visualisation

# Step 1: Analyze privacy policy
input_file = 'data/company_privacy.html'
main_pipeline.llm_pipeline(input_file)

# Step 2: Generate visualizations
main_pipeline_visualisation.run('company', 'company')
```

### Custom Analysis
```python
import cleaned_framework.html2text as h2t
import cleaned_framework.groq_client as gc
import cleaned_framework.rag as rag
import cleaned_framework.agent_llm as agent

# 1. Extract text
segments = h2t.extract_and_process_text_from_file('policy.html')

# 2. Initialize client and indexes
client = gc.getGroqClient('GROQ_API_KEY')
docs = rag.convert_json('kb/data_categories_kt.json')
index = rag.indexingHuggingfaceEmbedding(docs, 'data_index/')

# 3. Process each segment
for segment in segments:
    # Identify data flows
    _, flows = agent.selecting_paragraph_get_data_flows(client, segment)
    
    if flows != 'NO':
        # Categorize using RAG
        results = rag.retrieving(index, segment)
        # ... further processing
```

## 📊 Output Files

### From main_pipeline.py
| File | Description |
|------|-------------|
| `*_segment.csv` | Extracted text segments with indices |
| `*_completed_revised_new.csv` | Complete analysis results with all categorizations |

### From main_pipeline_visualisation.py
| File | Description |
|------|-------------|
| `*_verification_v2.csv` | Random samples for verification |
| `*_metrics_new_v2.csv` | Network analysis metrics |
| `*_basics_new_v2.csv` | Basic statistics (nodes, edges, parties) |
| `*_between_v2.csv` | Betweenness centrality analysis |
| `*_close_v2.csv` | Closeness centrality analysis |
| `*_central_v2.csv` | Degree centrality analysis |
| `*_tree_v2.csv` | Tree structure analysis |
| `*_longest_path_v2.csv` | Longest path analysis |
| `*_longest_path_length_v2.csv` | Path length statistics |
| `*_most_inwards_v2.csv` | Highest in-degree nodes |
| `*_most_outwards_v2.csv` | Highest out-degree nodes |
| `*.html` | Interactive network visualizations |

## ⚙️ Configuration

### API Rate Limiting
The framework uses sleep delays for rate limiting:
- 5 seconds between most API calls
- 10 seconds between text segments

### Knowledge Base Locations
Required KB files in `kb/`:
- `data_categories_kt.json`
- `data_consumer_type_kt.json`
- `data_processing_purpose_kt.json`
- `data_processing_method_kt.json`

### Model Configuration
Default models used:
- Data flow extraction: `llama-3.3-70b-versatile`
- Data categorization: `llama3-70b-8192`
- Party/purpose/method: `llama-3.1-8b-instant`
- Embeddings: `BAAI/bge-small-en-v1.5`

## 🐛 Troubleshooting

### Import Errors
```python
# Ensure you're importing from cleaned_framework
import cleaned_framework.rag as rag  # ✅ Correct
import revised_framework.rag as rag  # ❌ Old framework
```

### Missing Dependencies
```bash
# Install required packages
pip install groq llama-index beautifulsoup4 pypdf networkx pyvis spacy inflect pydantic numpy

# Download spaCy model
python -m spacy download en_core_web_sm
```

### API Key Issues
```python
# Ensure API key file exists and is readable
# File should contain only the API key, no extra whitespace
```

### Index Loading Errors
```python
# Indexes are created on first run and cached
# Delete index directories to regenerate if corrupted
```

## 💡 Tips

1. **Batch Processing**: Process multiple policies in a loop
2. **Result Caching**: Indexes are cached automatically
3. **Error Handling**: Each segment is try-catch wrapped
4. **Rate Limits**: Adjust sleep times if hitting API limits
5. **Memory**: Large policies may require chunking

## 📞 Support

- Check `README.md` for detailed documentation
- Review `CLEANUP_SUMMARY.md` for changes from original
- Refer to individual module docstrings for detailed API info
