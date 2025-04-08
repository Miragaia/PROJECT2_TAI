import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import os
import glob
import shutil

# Create output directory if it doesn't exist
output_dir = "complexity_profile_plot"
if os.path.exists(output_dir):
    # Delete and recreate the directory to ensure it's empty
    print(f"Deleting and recreating '{output_dir}' directory...")
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)
else:
    # Create the directory if it doesn't exist
    print(f"Creating '{output_dir}' directory...")
    os.makedirs(output_dir)

# Get all CSV files from the complexity_profile folder
csv_files = glob.glob("complexity_profile/*.csv")

for csv_file in csv_files:
    # Extract filename for use in plot titles and output filenames
    filename = os.path.basename(csv_file)
    base_filename = os.path.splitext(filename)[0]
    
    print(f"Processing {filename}...")
    
    # Load the complexity profile
    df = pd.read_csv(csv_file, quotechar='"')
    
    # Select a sequence to plot
    sequence_id = df["SequenceID"].unique()[0]
    df_seq = df[df["SequenceID"] == sequence_id]

    k_value = df["K"].unique()[0]

    start_position = k_value
    df_seq = df_seq[df_seq["Position"] >= start_position]
    
    # Extract data
    positions = df_seq["Position"].values
    complexity = df_seq["Complexity"].values
    
    # Calculate adaptive window size (approximately 5% of data length, must be odd)
    data_length = len(complexity)
    window_size = max(int(data_length * 0.05), 3)
    # Ensure window size is odd
    if window_size % 2 == 0:
        window_size += 1
    
    print(f"  Using adaptive window size: {window_size} for data length: {data_length}")
    
    # Apply low-pass filtering with Blackman window
    blackman_window = np.blackman(window_size)
    blackman_window /= blackman_window.sum()  # Normalize
    
    # Pad the signal to deal with edge effects
    padded = np.pad(complexity, (window_size//2, window_size//2), mode='edge')
    filtered = signal.convolve(padded, blackman_window, mode='valid')
    
    # Reverse direction filtering
    reversed_signal = np.flip(complexity)
    padded_reversed = np.pad(reversed_signal, (window_size//2, window_size//2), mode='edge')
    filtered_reversed = signal.convolve(padded_reversed, blackman_window, mode='valid')
    filtered_reversed = np.flip(filtered_reversed)
    
    # Combine by taking the minimum at each point
    combined = np.minimum(filtered, filtered_reversed)
    
    # Plot all stages
    plt.figure(figsize=(15, 10))
    
    plt.subplot(2, 1, 1)
    plt.plot(positions, complexity, color='green')
    plt.title(f'Original Complexity Profile for {sequence_id}')
    plt.ylabel('Complexity (bits)')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.subplot(2, 1, 2)
    plt.plot(positions, filtered, color='blue')
    plt.title(f'Filtered with Adaptive Blackman Window (size {window_size})')
    plt.ylabel('Complexity (bits)')
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    all_stages_filename = os.path.join(output_dir, f"{base_filename}_filtered_all.png")
    plt.savefig(all_stages_filename)
    plt.close()  # Close the figure to free memory
    
    print(f"Saved plots for {filename}")

print(f"All complexity profiles processed. Results saved in '{output_dir}' folder.")