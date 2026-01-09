"""
Setup Validation Script

Run this script to verify that your environment is correctly configured
for the Privacy Policy Analysis Framework.

Usage:
    python validate_setup.py
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)


def print_status(check_name, passed, message=""):
    """Print a check status."""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    
    print(f"{color}{status}{reset} {check_name}")
    if message:
        print(f"  {message}")


def check_python_version():
    """Check if Python version is 3.9+."""
    version = sys.version_info
    passed = version.major == 3 and version.minor >= 9
    message = f"Python {version.major}.{version.minor}.{version.micro}"
    if not passed:
        message += " (Need Python 3.9 or higher)"
    return passed, message


def check_dependencies():
    """Check if required Python packages are installed."""
    required_packages = [
        ('groq', 'Groq API client'),
        ('llama_index', 'LlamaIndex'),
        ('bs4', 'BeautifulSoup4'),
        ('pypdf', 'PyPDF'),
        ('networkx', 'NetworkX'),
        ('pyvis', 'PyVis'),
        ('spacy', 'spaCy'),
        ('pydantic', 'Pydantic'),
        ('numpy', 'NumPy'),
        ('inflect', 'Inflect'),
    ]
    
    results = []
    all_passed = True
    
    for package, name in required_packages:
        try:
            __import__(package)
            results.append((name, True, "Installed"))
        except ImportError:
            results.append((name, False, "Not installed"))
            all_passed = False
    
    return all_passed, results


def check_spacy_model():
    """Check if spaCy English model is downloaded."""
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        return True, "Model loaded successfully"
    except Exception as e:
        return False, f"Model not found. Run: python -m spacy download en_core_web_sm"


def check_api_key():
    """Check if Groq API key file exists."""
    # Check in parent directory
    parent_key = Path('../GROQ_API_KEY')
    current_key = Path('GROQ_API_KEY')
    
    if parent_key.exists():
        return True, f"Found in parent directory: {parent_key.resolve()}"
    elif current_key.exists():
        return True, f"Found in current directory: {current_key.resolve()}"
    else:
        return False, "GROQ_API_KEY file not found"


def check_directories():
    """Check if required directories exist or can be created."""
    required_dirs = ['data', 'kb', 'results']
    results = []
    all_passed = True
    
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists():
            results.append((dir_name, True, "Exists"))
        else:
            results.append((dir_name, False, f"Not found (will be created)"))
    
    return True, results  # Always pass, dirs can be created


def check_knowledge_bases():
    """Check if knowledge base files exist."""
    kb_files = [
        'kb/data_categories_kt.json',
        'kb/data_consumer_type_kt.json',
        'kb/data_processing_purpose_kt.json',
        'kb/data_processing_method_kt.json',
    ]
    
    results = []
    all_passed = True
    
    for kb_file in kb_files:
        path = Path(kb_file)
        if path.exists():
            results.append((kb_file, True, "Found"))
        else:
            results.append((kb_file, False, "Missing"))
            all_passed = False
    
    return all_passed, results


def check_data_files():
    """Check if any privacy policy files exist."""
    data_path = Path('data')
    if not data_path.exists():
        return False, "data/ directory not found"
    
    html_files = list(data_path.glob('*.html')) + list(data_path.glob('*.htm'))
    pdf_files = list(data_path.glob('*.pdf'))
    all_files = html_files + pdf_files
    
    if all_files:
        return True, f"Found {len(all_files)} policy file(s)"
    else:
        return False, "No .html or .pdf files found in data/"


def main():
    """Run all validation checks."""
    print_header("Privacy Policy Analysis Framework - Setup Validation")
    
    total_checks = 0
    passed_checks = 0
    
    # Python version
    print_header("Python Version")
    passed, message = check_python_version()
    print_status("Python Version", passed, message)
    total_checks += 1
    if passed:
        passed_checks += 1
    
    # Dependencies
    print_header("Python Dependencies")
    all_passed, results = check_dependencies()
    for name, passed, message in results:
        print_status(name, passed, message)
        total_checks += 1
        if passed:
            passed_checks += 1
    
    # spaCy model
    print_header("spaCy Language Model")
    passed, message = check_spacy_model()
    print_status("en_core_web_sm", passed, message)
    total_checks += 1
    if passed:
        passed_checks += 1
    
    # API key
    print_header("API Configuration")
    passed, message = check_api_key()
    print_status("Groq API Key", passed, message)
    total_checks += 1
    if passed:
        passed_checks += 1
    
    # Directories
    print_header("Directory Structure")
    all_passed, results = check_directories()
    for name, passed, message in results:
        print_status(name, passed, message)
    # Note: We don't count individual directories
    
    # Knowledge bases
    print_header("Knowledge Bases")
    all_passed, results = check_knowledge_bases()
    for name, passed, message in results:
        print_status(name, passed, message)
        total_checks += 1
        if passed:
            passed_checks += 1
    
    # Data files
    print_header("Input Data")
    passed, message = check_data_files()
    print_status("Privacy Policy Files", passed, message)
    total_checks += 1
    if passed:
        passed_checks += 1
    
    # Summary
    print_header("Validation Summary")
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    print(f"\nPassed: {passed_checks}/{total_checks} ({percentage:.1f}%)")
    
    if passed_checks == total_checks:
        print("\n🎉 All checks passed! You're ready to run the framework.")
        print("\nNext steps:")
        print("  1. Run: python example_usage.py")
        print("  2. Or see GETTING_STARTED.md for detailed instructions")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        print("\nRecommended actions:")
        print("  1. Install missing dependencies: pip install -r requirements.txt")
        print("  2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("  3. Create GROQ_API_KEY file with your API key")
        print("  4. Add knowledge base files to kb/ directory")
        print("  5. See GETTING_STARTED.md for detailed setup instructions")
    
    print()


if __name__ == "__main__":
    main()
