# LADFA: A Framework using (L)LMs and R(A)G for Personal (D)ata (F)low (A)nalysis in Privacy Policies

This guide will help you set up and run the privacy policy analysis framework for the first time.

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Setup](#setup)
4. [Quick Start](#quick-start)
5. [Advanced Usage](#advanced-usage)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Python 3.9 or higher
- 8GB RAM minimum (16GB recommended for large policies)
- Internet connection (for LLM API calls and downloading models)

### Required Accounts
- **Groq API Account**: Sign up at [https://console.groq.com](https://console.groq.com)
  - Get your API key from the dashboard
  - Free tier available with rate limits

## Installation

### Step 1: Clone or Download the Repository
```bash
cd /path/to/your/workspace
# If you have the code already, skip to next step
```

### Step 2: Install Python Dependencies
```bash
cd cleaned_framework
pip install -r requirements.txt
```

### Step 3: Download spaCy Language Model
```bash
python -m spacy download en_core_web_sm
```

## Setup

### Step 1: Configure API Key

Create a file named `GROQ_API_KEY` in the parent directory (not inside cleaned_framework):
```bash
cd /path/to/hri-llm
echo "your_groq_api_key_here" > GROQ_API_KEY
```

**Important**: Keep your API key secure and never commit it to version control!

### Step 2: Prepare Knowledge Bases

Create a `kb/` directory and add the required knowledge base JSON files:

```bash
mkdir -p kb
```

Required files:
- `kb/data_categories_kt.json` - Categories of personal data types
- `kb/data_consumer_type_kt.json` - Types of data collection parties/consumers
- `kb/data_processing_purpose_kt.json` - Purposes for data processing
- `kb/data_processing_method_kt.json` - Methods of data processing/collection

**Knowledge Base Format Example** (`data_categories_kt.json`):
```json
[
  {
    "data_type": "email address",
    "category": "Contact Information",
    "description": "Electronic mail address used for communication"
  },
  {
    "data_type": "IP address",
    "category": "Technical Data",
    "description": "Internet Protocol address identifying device"
  }
]
```

### Step 3: Prepare Privacy Policy Files

Place your privacy policy files in the `data/` directory:

```bash
mkdir -p data
# Copy your HTML or PDF privacy policies to data/
cp /path/to/policy.html data/
```

Supported formats:
- HTML files (`.html`, `.htm`)
- PDF files (`.pdf`)

### Step 4: Create Results Directory

```bash
mkdir -p results
```

## Quick Start

### Option 1: Using the Example Script (Recommended for Beginners)

Run the interactive example script:
```bash
python example_usage.py
```

This will launch an interactive menu where you can:
1. Check prerequisites
2. Analyze privacy policies
3. Generate visualizations
4. Run complete workflows

### Option 2: Direct Python Import

**Analyze a single privacy policy:**
```python
import cleaned_framework.main_pipeline as pipeline

# Analyze HTML file
pipeline.llm_pipeline('data/example_policy.html')

# Analyze PDF file
pipeline.llm_pipeline('data/example_policy.pdf')
```

**Generate visualizations:**
```python
import cleaned_framework.main_pipeline_visualisation as viz

# Generate all visualizations and metrics
# First parameter: policy name identifier
# Second parameter: main party/company name
viz.run('example', 'example_company')
```

### Option 3: Command Line Quick Test

Test a single file:
```bash
python -c "import cleaned_framework.main_pipeline as p; p.llm_pipeline('data/vauxhall_clean.html')"
```

## Advanced Usage

### Batch Processing Multiple Policies

Create a custom script:
```python
import cleaned_framework.main_pipeline as pipeline

policies = [
    'data/audi_clean.html',
    'data/ford_clean.html',
    'data/honda_clean.html',
]

for policy in policies:
    print(f"Processing {policy}...")
    try:
        pipeline.llm_pipeline(policy)
        print(f"✓ Completed {policy}")
    except Exception as e:
        print(f"✗ Failed {policy}: {e}")
```

### Customizing Analysis Parameters

Edit `main_pipeline.py` to adjust:
- **LLM Model**: Change `modelID` parameter (e.g., `llama-3.3-70b-versatile`, `llama3-70b-8192`)
- **Sleep Duration**: Adjust `time.sleep()` values to match your API rate limits
- **Top-K Retrieval**: Modify `top_k` parameter in RAG retrieval calls
- **Embedding Model**: Change in `indexingHuggingfaceEmbedding()` calls

### Customizing Visualizations

Edit `main_pipeline_visualisation.py` to adjust:
- **Centrality Measure**: Change `option` variable (`'betweenness'`, `'closeness'`, `'degree'`)
- **Top N Nodes**: Modify `top_n` value (default: 10)
- **Output File Names**: Adjust file path variables

## Understanding the Output

### Analysis Pipeline Outputs

For input file `data/example_clean.html`, you get:

1. **`data/example_clean_segment.csv`**
   - Text segments extracted from the privacy policy
   - Columns: `index`, `text`

2. **`data/example_clean_completed_revised_new.csv`**
   - Complete analysis results with data flows
   - Columns:
     - `text_idx`: Segment index
     - `data_type`: Type of data identified
     - `data_category`: Categorized data type
     - `data_flow`: JSON representation of data flow
     - `data_collection_party`: Who collects the data
     - `data_collection_purpose`: Why data is collected
     - `data_collection_method`: How data is collected

### Visualization Pipeline Outputs

For policy name `example`, outputs are in `results/`:

1. **Network Metrics**:
   - `example_metrics_new_v2.csv` - Overall network statistics
   - `example_basics_new_v2.csv` - Basic graph properties
   - `example_between_v2.csv` - Betweenness centrality
   - `example_close_v2.csv` - Closeness centrality
   - `example_central_v2.csv` - Degree centrality

2. **Path Analysis**:
   - `example_longest_path_v2.csv` - Longest paths in network
   - `example_longest_path_length_v2.csv` - Path lengths
   - `example_tree_v2.csv` - Tree structure analysis

3. **Degree Analysis**:
   - `example_most_inwards_v2.csv` - Nodes with most incoming edges
   - `example_most_outwards_v2.csv` - Nodes with most outgoing edges

4. **Visualizations**:
   - Interactive HTML network graphs (open in browser)

## Workflow Best Practices

### 1. Start Small
- Test with one simple privacy policy first
- Verify outputs before batch processing
- Check API rate limits

### 2. Monitor API Usage
- Groq API has rate limits (check your plan)
- Default script includes `time.sleep()` delays
- Adjust delays based on your quota

### 3. Validate Knowledge Bases
- Ensure KB files are properly formatted JSON
- Keep categories consistent
- Update KBs as you discover new patterns

### 4. Organize Results
- Create subdirectories for different analysis runs
- Use consistent naming conventions
- Keep raw and processed results separate

### 5. Iterative Improvement
- Review incorrect categorizations
- Update knowledge bases with new categories
- Refine prompts in `agent_llm.py` if needed

## Troubleshooting

### Common Issues

**1. "API key not found" error**
- Ensure `GROQ_API_KEY` file exists in parent directory
- Check file has no extra whitespace or newlines
- Verify API key is valid

**2. "Knowledge base not found" error**
- Verify `kb/` directory exists
- Check all 4 required JSON files are present
- Ensure JSON files are properly formatted

**3. Rate limit errors**
- Increase `time.sleep()` values in `main_pipeline.py`
- Check your Groq API quota
- Consider using a different model with higher limits

**4. Out of memory errors**
- Process smaller policies first
- Reduce batch size
- Clear vector indexes and regenerate

**5. Import errors**
- Reinstall requirements: `pip install -r requirements.txt --force-reinstall`
- Check Python version: `python --version` (need 3.9+)
- Install spaCy model: `python -m spacy download en_core_web_sm`

**6. Visualization not generating**
- Ensure analysis results exist in `results/` directory
- Check file naming matches expected format
- Verify CSV files are not corrupted

### Getting Help

1. Check existing documentation:
   - `README.md` - Full framework documentation
   - `QUICK_REFERENCE.md` - Quick command reference
   - `CLEANUP_SUMMARY.md` - Code structure overview

2. Review error messages carefully:
   - Python stack traces show exact error location
   - API errors often include specific fix instructions

3. Enable debug output:
   - Add print statements in pipeline scripts
   - Check intermediate CSV outputs
   - Verify knowledge base loading

## Next Steps

Once you have the basic pipeline working:

1. **Expand Knowledge Bases**: Add more categories and examples
2. **Customize Prompts**: Modify `agent_llm.py` for better accuracy
3. **Build Dashboards**: Create custom visualizations of results
4. **Automate Workflows**: Set up scheduled analysis runs
5. **Compare Policies**: Analyze differences across companies

## Additional Resources

- **Groq Documentation**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **LlamaIndex Docs**: [https://docs.llamaindex.ai](https://docs.llamaindex.ai)
- **NetworkX Guide**: [https://networkx.org/documentation/stable/](https://networkx.org/documentation/stable/)
- **spaCy Documentation**: [https://spacy.io/usage](https://spacy.io/usage)

---

**Happy Analyzing! 🚀**

If you encounter any issues not covered here, please check the code comments or raise an issue.
