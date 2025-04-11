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

# Plot
plt.figure(figsize=(15, 6))
plt.plot(positions1, complexity1, label=f"{id1}", color='green')
plt.plot(positions2, complexity2, label=f"{id2}", color='orange')
plt.title(f"Smoothed Complexity Profiles (window=101): {id1} vs {id2}")
plt.xlabel("Position")
plt.ylabel("Complexity (bits)")
plt.ylim(0,2.0)
plt.grid(True, linestyle='--')
plt.legend()

plt.tight_layout()
output_path = "complexity_profile_plot/comparison_smoothed_large_window.png"
plt.savefig(output_path)
plt.show()

print(f"Saved smoothed comparison plot to {output_path}")
