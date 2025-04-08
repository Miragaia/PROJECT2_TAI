import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

# Load the complexity profile
df = pd.read_csv("complexity_profile/complexity_gi|49169782|ref|NC_005831.2|_Human_Coronavirus_NL63,_complete_genome.csv", quotechar='"')

# Select a sequence to plot
sequence_id = df["SequenceID"].unique()[0]
df_seq = df[df["SequenceID"] == sequence_id]

# Extract data
positions = df_seq["Position"].values
complexity = df_seq["Complexity"].values

# Apply low-pass filtering with Blackman window
window_size = 21  # Size of the window
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

plt.subplot(3, 1, 1)
plt.plot(positions, complexity, color='green')
plt.title(f'Original Complexity Profile for {sequence_id}')
plt.ylabel('Complexity (bits)')
plt.grid(True, linestyle='--', alpha=0.6)

plt.subplot(3, 1, 2)
plt.plot(positions, filtered, color='blue')
plt.title('Filtered with Blackman Window (size 21)')
plt.ylabel('Complexity (bits)')
plt.grid(True, linestyle='--', alpha=0.6)

plt.subplot(3, 1, 3)
plt.plot(positions, combined, color='black')
plt.title('Combined Minimum from Both Directions')
plt.xlabel('Position (bp)')
plt.ylabel('Complexity (bits)')
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("complexity_profile_filtered_all.png")
plt.show()

# Optional: save just the final combined one
plt.figure(figsize=(12, 5))
plt.plot(positions, combined, color='black')
plt.title(f'Processed Complexity Profile for {sequence_id}')
plt.xlabel("Position (bp)")
plt.ylabel("Complexity (bits)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("complexity_profile_processed_only.png")
plt.show()
