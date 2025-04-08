#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import csv
import os

def create_numbered_mapping(df):
    """Create a mapping of sequence IDs to numbers and a new DataFrame with numbers as labels"""
    # Create the mapping
    sequence_ids = df.index.tolist()
    id_to_number = {seq_id: f"#{i+1}" for i, seq_id in enumerate(sequence_ids)}
    
    # Create a new DataFrame with numbered labels
    df_numbered = df.copy()
    df_numbered.index = [id_to_number[idx] for idx in df_numbered.index]
    df_numbered.columns = [id_to_number[col] for col in df_numbered.columns]
    
    return df_numbered, id_to_number

def write_sequence_key(id_to_number, output_file):
    """Write a key file mapping numbers to full sequence names"""
    with open(output_file, 'w') as f:
        f.write("Number,Sequence ID\n")
        for seq_id, number in id_to_number.items():
            f.write(f"{number},\"{seq_id}\"\n")
    
    print(f"Sequence ID key saved to {output_file}")

def plot_similarity_heatmap(similarity_df, output_file):
    """Create and save a heatmap of sequence similarities"""
    plt.figure(figsize=(14, 12))
    
    # Create a custom colormap (low values = more similar)
    cmap = sns.color_palette("viridis_r", as_cmap=True)
    
    # Plot the heatmap with smaller font size for annotations
    ax = sns.heatmap(similarity_df, annot=True, fmt=".3f", cmap=cmap,
                     linewidths=0.5, cbar_kws={'label': 'NRC (Lower = More Similar)'},
                     annot_kws={"size": 8})
    
    plt.title("Sequence Similarity Matrix (NRC Values)", fontsize=16)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    plt.close()
    
    print(f"Similarity heatmap saved to {output_file}")

def main():
    # Get CSV file path from command line argument
    if len(sys.argv) < 2:
        print("Usage: python visualize.py <csv_file> [output_prefix]")
        return
        
    csv_file = sys.argv[1]
    
    # Get the directory of the input file
    file_dir = os.path.dirname(csv_file)
    
    # Define output prefix based on input file name but in the same directory
    file_name = os.path.basename(csv_file)
    base_name = os.path.splitext(file_name)[0]
    output_prefix = os.path.join(file_dir, base_name)
    
    if len(sys.argv) > 2:
        # If user specified a prefix, use it (but still in the same directory)
        custom_prefix = sys.argv[2]
        output_prefix = os.path.join(file_dir, custom_prefix)
    
    print(f"Loading similarity matrix from {csv_file}...")
    print(f"Output files will be saved to the folder: {file_dir}")
    
    try:
        # Try with default parameters first
        df = pd.read_csv(csv_file, index_col=0)
    except ValueError as e:
        print(f"Error with default parsing: {e}")
        print("Trying with explicit quoting settings...")
        
        # Try again with explicit quoting parameters
        df = pd.read_csv(csv_file, index_col=0, quoting=csv.QUOTE_NONNUMERIC)
    
    # Convert all data to float
    try:
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.fillna(1.0, inplace=True)
    except Exception as e:
        print(f"Warning while converting data: {e}")
    
    # Create numbered mapping
    df_numbered, id_to_number = create_numbered_mapping(df)
    
    # Write key file
    key_file = f"{output_prefix}_key.csv"
    write_sequence_key(id_to_number, key_file)
    
    # Create visualizations
    print("Creating visualizations...")
    plot_similarity_heatmap(df_numbered, f"{output_prefix}_heatmap.png")
    
    print("\nDone! Visualization files created:")
    print(f"1. {output_prefix}_heatmap.png - Standard heatmap")
    print(f"2. {output_prefix}_key.csv - Key file mapping numbers to sequence IDs")
    print("\nUse the key file to reference the full sequence names.")

if __name__ == "__main__":
    main()