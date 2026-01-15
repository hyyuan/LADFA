"""
Main Pipeline Visualization Script

This script runs post-processing on privacy policy analysis results to generate
network visualizations and statistical outputs. It processes multiple privacy
policies in batch, creating various metrics and graph analyses.

For each privacy policy, it generates:
- Network graphs with different centrality measures
- Statistical metrics CSV files
- Path analysis and tree structures
- In/out-degree analysis
"""

import post_processor as processor


def run(name, main_party):
    """
    Run complete post-processing pipeline for a single privacy policy.
    
    This function generates two types of outputs:
    1. Full post-processing with verification sampling
    2. Simple post-processing with multiple network metrics
    
    Args:
        name (str): Name identifier for the privacy policy (e.g., 'renault', 'audi')
        main_party (str): Main party name (usually same as name, lowercase)
    """
    # Define input and output file paths
    input_file = 'results/' + name + '_output.csv'
    csv_file = 'results/' + name + '_segment.csv'
    
    # Configuration for network analysis
    option = 'betweenness'  # Centrality measure to use
    top_n = 10  # Number of top nodes to highlight
    
    # Output files for full post-processing
    verification_csv = 'results/' + name + '_verification_v2.csv'
    metrics_csv = 'results/' + name + '_metrics_new_v2.csv'
    basics_csv = 'results/' + name + '_basics_new_v2.csv'
    
    # Run full post-processing with verification sampling
    processor.post_processing(
        input_file, 
        main_party, 
        csv_file, 
        option, 
        top_n, 
        verification_csv, 
        metrics_csv, 
        basics_csv
    )
    
    # Output files for simple post-processing (multiple metrics)
    between_csv = 'results/' + name + '_between.csv'
    close_csv = 'results/' + name + '_close.csv'
    central_csv = 'results/' + name + '_central.csv'
    tree_csv = 'results/' + name + '_tree.csv'
    longest_path_csv = 'results/' + name + '_longest_path.csv'
    longest_path_length_csv = 'results/' + name + '_longest_path_length.csv'
    most_inwards_csv = 'results/' + name + '_most_inwards.csv'
    most_outwards_csv = 'results/' + name + '_most_outwards.csv'
    
    # Run simple post-processing with various network metrics
    processor.post_processing_simple(
        input_file, 
        main_party, 
        csv_file, 
        top_n, 
        between_csv, 
        close_csv, 
        central_csv, 
        tree_csv, 
        longest_path_csv, 
        longest_path_length_csv, 
        most_inwards_csv, 
        most_outwards_csv
    )


if __name__ == "__main__":
    # Batch process multiple privacy policies
    run('kia', 'kia')
