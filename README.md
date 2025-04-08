# PROJECT2_TAI

## Algorithmic Theory of Information — 1st Year MEI (2nd Semester)  
University of Aveiro

This project implements a Finite-Context Model (FCM) for DNA sequence similarity analysis. The model is trained on reference sequences and used to evaluate and rank DNA sequences based on their compression efficiency.

---

## How It Works

1. **Model Training:** Builds an FCM using sequences from `meta.txt`.
2. **Model Freezing:** Locks the model to prevent further learning.
3. **Sequence Extraction:** Loads DNA sequences and labels from `db.txt`.
4. **Compression Calculation:** Computes the number of bits needed to encode each sequence using the trained model.
5. **NRC Score Computation:** Calculates Normalized Relative Compression (NRC) scores.
6. **Sorting & Output:** Sorts sequences by ascending NRC score (lower NRC = higher similarity) and displays the top matches.

---

## Compilation and Execution

### Compile
```bash
g++ -o MetaClass MetaClass.cpp -std=c++17 -O2
```

### Run
```bash
./MetaClass -cp -d db.txt -s meta.txt -k 14 -a 0.1 -t 20 -c similarity_matrix.csv
```

Arguments:
- `-d`: Database file containing DNA sequences.
- `-s`: Meta file for training.
- `-k`: Context length (k-mer size).
- `-a`: Alpha smoothing parameter.
- `-t`: Number of top matches to display.
- `-c`: Output CSV file for similarity matrix.
- `-cp`: Flag to generate complexity profiles.

---

## Running Tests and Generating Plots

### Setup Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Requirements
```bash
pip install -r requirements.txt
```

### Run Experiments
```bash
python3 save_results.py -d db.txt -s meta.txt --k_values 3,4,5,6,7,8 --alpha_values 0.01,0.1,1.0 -o results.json
```

Options:
- `--k_values`: List of k-values to test.
- `--alpha_values`: List of alpha values to test.
- `-o`: Output file to save results.

### Visualize Results
```bash
python3 visualize_results.py results.json -d output_plots
```

- `-d`: Directory to store output plots.

### Visualize Sequence Similarity
```bash
python3 sequence_similarity.py similarity_matrix/similarity_matrix.csv
```

### Visualize Complexity profiles
```bash
python3 complexity.py
```

