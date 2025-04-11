import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def load_and_smooth(csv_file, window_size=2000):
    df = pd.read_csv(csv_file, quotechar='"')
    sequence_id = df["SequenceID"].unique()[0]
    k_value = df["K"].unique()[0]
    df_seq = df[df["SequenceID"] == sequence_id]
    df_seq = df_seq[df_seq["Position"] >= k_value]

    positions = df_seq["Position"].values
    complexity = df_seq["Complexity"].values

    # Suavização com média móvel (janela maior)
    window = np.ones(window_size) / window_size
    smoothed = np.convolve(complexity, window, mode='same')

    return positions, smoothed, sequence_id

# Arquivos
file1 = "complexity_profile/complexity_NC_005831.2_Human_Coronavirus_NL63,_complete_genome.csv"
file2 = "complexity_profile/complexity_gi|49169782|ref|NC_005831.2|_Human_Coronavirus_NL63,_complete_genome.csv"

positions1, complexity1, id1 = load_and_smooth(file1)
positions2, complexity2, id2 = load_and_smooth(file2)

# Calculate mean of each line
mean1 = np.mean(complexity1)
mean2 = np.mean(complexity2)

# Calculate the combined mean (single value) of both sequences
combined_values = np.concatenate([complexity1, complexity2])
overall_mean = np.mean(combined_values)

# Plot
plt.figure(figsize=(15, 6))
plt.plot(positions1, complexity1, label=f"{id1}", color='green')
plt.plot(positions2, complexity2, label=f"{id2}", color='orange')

# Plot mean lines
plt.axhline(y=mean1, color='darkgreen', linestyle='--', label=f'Mean of {id1}: {mean1:.3f}')
plt.axhline(y=mean2, color='darkorange', linestyle='--', label=f'Mean of {id2}: {mean2:.3f}')

# Plot overall mean line (straight horizontal line)
plt.axhline(y=overall_mean, color='red', linestyle='-', label=f'Mean of both sequences: {overall_mean:.3f}')

plt.title(f"Complexity Profiles Comparison with Means")
plt.xlabel("Position")
plt.ylabel("Complexity (bits)")
plt.ylim(0, 2.0)
plt.grid(True, linestyle='--')
plt.legend()

plt.tight_layout()
output_path = "complexity_profile_plot/comparison_with_means.png"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
plt.savefig(output_path)
plt.show()

print(f"Saved comparison plot with means to {output_path}")