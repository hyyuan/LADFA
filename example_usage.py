"""
Example Usage Script - Privacy Policy Analysis Framework

This script demonstrates how to use the main functions of the privacy policy
analysis framework, including both analysis and visualization pipelines.

QUICK START:
1. Ensure all dependencies are installed (see requirements.txt)
2. Set up your Groq API key in a file (default: 'GROQ_API_KEY')
3. Place knowledge base JSON files in 'kb/' directory
4. Place your privacy policy files (HTML/PDF) in 'data/' directory
5. Run this script and follow the prompts

WORKFLOW:
- Step 1: Analyze privacy policies → Generate CSV results
- Step 2: Visualize results → Generate network graphs and metrics
"""

import os
import sys
from pathlib import Path

# Import the main pipeline modules
import cleaned_framework.main_pipeline as main_pipeline
import cleaned_framework.main_pipeline_visualisation as visualisation


def setup_directories():
    """
    Create necessary directories if they don't exist.
    This ensures smooth operation of the pipeline.
    """
    directories = [
        'data',           # Input privacy policy files
        'kb',             # Knowledge base JSON files
        'results',        # Output CSV and visualization files
        'data_categories_index',
        'data_consumer_index',
        'data_processing_purpose_index',
        'data_processing_method_index'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
    print("✓ Directory structure verified")


def check_prerequisites():
    """
    Check if required files and dependencies exist.
    Returns True if all prerequisites are met.
    """
    print("\n=== Checking Prerequisites ===\n")
    
    issues = []
    
    # Check for API key
    if not os.path.exists('GROQ_API_KEY'):
        issues.append("❌ GROQ_API_KEY file not found")
    else:
        print("✓ GROQ API key file found")
    
    # Check for knowledge bases
    kb_files = [
        'kb/data_categories_kt.json',
        'kb/data_consumer_type_kt.json',
        'kb/data_processing_purpose_kt.json',
        'kb/data_processing_method_kt.json'
    ]
    
    for kb_file in kb_files:
        if not os.path.exists(kb_file):
            issues.append(f"❌ Knowledge base missing: {kb_file}")
        else:
            print(f"✓ Knowledge base found: {kb_file}")
    
    # Check for input data
    data_files = list(Path('data').glob('*.html')) + list(Path('data').glob('*.htm')) + list(Path('data').glob('*.pdf'))
    if not data_files:
        issues.append("⚠️  No privacy policy files found in data/ directory")
    else:
        print(f"✓ Found {len(data_files)} privacy policy file(s) in data/")
    
    if issues:
        print("\n=== Issues Found ===")
        for issue in issues:
            print(issue)
        return False
    
    print("\n✓ All prerequisites met!")
    return True


def analyze_single_policy(file_path):
    """
    Analyze a single privacy policy file.
    
    This function runs the main analysis pipeline on one file.
    Results are saved as CSV files with the same base name as the input file.
    
    Args:
        file_path (str): Path to the HTML or PDF privacy policy file
        
    Output files:
        - {filename}_segment.csv: Text segments extracted from the policy
        - {filename}_completed_revised_new.csv: Complete analysis results
    """
    print(f"\n=== Analyzing: {file_path} ===\n")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        main_pipeline.llm_pipeline(file_path)
        print(f"\n✓ Analysis complete for {file_path}")
        print(f"  Results saved to: {os.path.splitext(file_path)[0]}_completed_revised_new.csv")
        return True
    except Exception as e:
        print(f"❌ Error analyzing {file_path}: {e}")
        return False


def visualize_results(policy_name, main_party_name):
    """
    Generate visualizations and metrics from analysis results.
    
    This function creates network graphs, statistical metrics, and various
    analyses from the CSV results produced by the analysis pipeline.
    
    Args:
        policy_name (str): Name identifier (e.g., 'audi', 'ford')
        main_party_name (str): Main party name (usually same as policy_name)
        
    Input required:
        - results/{policy_name}_clean_completed_revised_v2.csv
        - results/{policy_name}_clean_segment_v2.csv
        
    Output files:
        - Network visualizations (HTML)
        - Metrics CSV files (centrality, paths, degrees)
        - Verification samples
    """
    print(f"\n=== Generating Visualizations: {policy_name} ===\n")
    
    # Check if required input files exist
    required_files = [
        f'results/{policy_name}_clean_completed_revised_v2.csv',
        f'results/{policy_name}_clean_segment_v2.csv'
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    if missing:
        print(f"❌ Missing required files:")
        for f in missing:
            print(f"   - {f}")
        print("\n💡 Tip: Ensure analysis results are in results/ directory with correct naming")
        return False
    
    try:
        visualisation.run(policy_name, main_party_name)
        print(f"\n✓ Visualizations complete for {policy_name}")
        print(f"  Check results/ directory for outputs")
        return True
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")
        return False


def example_complete_workflow():
    """
    Example: Complete workflow for a single privacy policy.
    
    This demonstrates the full pipeline from raw policy to visualizations.
    """
    print("\n" + "="*60)
    print("EXAMPLE: Complete Analysis & Visualization Workflow")
    print("="*60)
    
    # Step 1: Analyze a privacy policy
    input_file = 'data/vauxhall_clean.html'
    success = analyze_single_policy(input_file)
    
    if not success:
        print("\n❌ Analysis failed. Please check the error messages above.")
        return
    
    # Step 2: Move results to expected location for visualization
    # (In practice, you may need to rename/move files to match expected names)
    print("\n💡 To generate visualizations:")
    print("   1. Move/rename analysis results to results/ directory")
    print("   2. Use naming format: {name}_clean_completed_revised_v2.csv")
    print("   3. Run visualisation.run('name', 'main_party')")
    
    # Example visualization call (uncomment when files are ready):
    # visualize_results('vauxhall', 'vauxhall')


def example_batch_analysis():
    """
    Example: Batch process multiple privacy policies.
    
    This is useful when you have multiple policies to analyze.
    """
    print("\n" + "="*60)
    print("EXAMPLE: Batch Analysis of Multiple Policies")
    print("="*60)
    
    # Get all HTML and PDF files from data directory
    policy_files = list(Path('data').glob('*.html')) + \
                   list(Path('data').glob('*.htm')) + \
                   list(Path('data').glob('*.pdf'))
    
    if not policy_files:
        print("❌ No policy files found in data/ directory")
        return
    
    print(f"\nFound {len(policy_files)} policy file(s):")
    for i, file in enumerate(policy_files, 1):
        print(f"  {i}. {file}")
    
    response = input("\nProcess all files? (y/n): ").strip().lower()
    
    if response == 'y':
        successful = 0
        failed = 0
        
        for file in policy_files:
            if analyze_single_policy(str(file)):
                successful += 1
            else:
                failed += 1
        
        print(f"\n=== Batch Analysis Complete ===")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
    else:
        print("Batch analysis cancelled.")


def example_batch_visualization():
    """
    Example: Generate visualizations for multiple policies.
    
    This processes all result files in the results/ directory.
    """
    print("\n" + "="*60)
    print("EXAMPLE: Batch Visualization")
    print("="*60)
    
    # List of policies to visualize (name, main_party)
    policies = [
        ('audi', 'audi'),
        ('ford', 'ford'),
        ('honda', 'honda'),
        ('kia', 'kia'),
        ('lexus', 'lexus'),
        ('nissan', 'nissan'),
        ('polestar', 'polestar'),
        ('renault', 'renault'),
        ('vauxhall', 'vauxhall'),
    ]
    
    print(f"\nConfigured to visualize {len(policies)} policies")
    print("Policies:", ', '.join([p[0] for p in policies]))
    
    response = input("\nGenerate visualizations for all? (y/n): ").strip().lower()
    
    if response == 'y':
        successful = 0
        failed = 0
        
        for name, party in policies:
            if visualize_results(name, party):
                successful += 1
            else:
                failed += 1
        
        print(f"\n=== Batch Visualization Complete ===")
        print(f"  Successful: {successful}")
        print(f"  Failed: {failed}")
    else:
        print("Batch visualization cancelled.")


def interactive_menu():
    """
    Interactive menu for users to choose what to do.
    """
    while True:
        print("\n" + "="*60)
        print("Privacy Policy Analysis Framework - Interactive Menu")
        print("="*60)
        print("\n1. Check Prerequisites")
        print("2. Analyze Single Policy")
        print("3. Batch Analyze All Policies")
        print("4. Generate Visualizations for Single Policy")
        print("5. Batch Generate Visualizations")
        print("6. Run Complete Workflow Example")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            check_prerequisites()
            
        elif choice == '2':
            file_path = input("\nEnter policy file path (e.g., data/example.html): ").strip()
            analyze_single_policy(file_path)
            
        elif choice == '3':
            example_batch_analysis()
            
        elif choice == '4':
            policy_name = input("\nEnter policy name (e.g., audi): ").strip()
            main_party = input("Enter main party name (usually same as above): ").strip()
            visualize_results(policy_name, main_party)
            
        elif choice == '5':
            example_batch_visualization()
            
        elif choice == '6':
            example_complete_workflow()
            
        elif choice == '7':
            print("\nGoodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please enter 1-7.")


def main():
    """
    Main entry point for the example script.
    """
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Privacy Policy Analysis Framework - Example Usage       ║
    ║                                                           ║
    ║  This script demonstrates how to use the framework for   ║
    ║  analyzing privacy policies and generating network       ║
    ║  visualizations of data flows.                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Setup directories
    setup_directories()
    
    # Launch interactive menu
    interactive_menu()


if __name__ == "__main__":
    main()
