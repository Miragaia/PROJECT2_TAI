import pandas as pd
import matplotlib.pyplot as plt

# Load data up to line 1241
df = pd.read_csv("complexity_profile/complexity_Super_ISS_Si1240.csv")

# Select a sequence to plot
sequence_id = df["SequenceID"].unique()[0]  # Choose first sequence
df_seq = df[df["SequenceID"] == sequence_id]

# Plot
plt.figure(figsize=(12, 5))
plt.plot(df_seq["Position"], df_seq["Complexity"], color="blue", linewidth=0.8)

# Labels
plt.xlabel("Position (bp)")
plt.ylabel("Complexity (bits per base)")
plt.title(f"Complexity Profile for {sequence_id}")
plt.grid()

# Save and show
plt.savefig("complexity_profile1.png")
plt.show()
