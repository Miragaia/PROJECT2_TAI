# PROJECT2_TAI

## First Year - MEI - 2nd Semester Class (Universidade de Aveiro)  
### Algorithmic Theory of Information

This project implements a finite-context model (FCM) for DNA sequence similarity analysis. It trains a model on reference sequences, then evaluates and ranks DNA sequences based on compression efficiency.

---

## How It Works:

1. **Model Training:** Trains a finite-context model (FCM) using `meta.txt`.
2. **Model Freezing:** Prevents further learning after training.
3. **Sequence Extraction:** Reads DNA sequences and their names from `db.txt`.
4. **Compression Calculation:** Computes the number of bits required to encode each sequence.
5. **NRC Score Computation:** Calculates Normalized Relative Compression (NRC) scores.
6. **Sorting & Output:** Sorts sequences in ascending NRC order (lower NRC = higher similarity) and prints the top 20 matches.

---

## Compilation & Execution

### Compile:
```bash
 g++ -o MetaClass MetaClass.cpp -std=c++17 -O2
```

### Run:
```bash
 ./MetaClass -d db.txt -s meta.txt -k 3 -a 0.1 -t 20
```
- `-d`: Database file containing DNA sequences.
- `-s`: Meta file for training.
- `-k`: Context length.
- `-a`: Alpha smoothing parameter.
- `-t`: Number of top matches to display.

---

## Running Tests & Generating Plots

### Setup Virtual Environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Requirements:
```bash
pip install -r requirements.txt
```

### Run Experiments:
```bash
python3 save_results.py -d db.txt -s meta.txt --k_values 3,4,5,6,7,8 --alpha_values 0.01,0.1,1.0 -o results.json
```
- `--k_values`: List of k-values to test.
- `--alpha_values`: List of alpha values to test.
- `-o`: Output file to save results.

### Visualize Results:
```bash
python3 visualize_results.py results.json -d output_plots
```
- `-d`: Directory to store output plots.


### Run Complexity Profile
```bash
g++ -o ComplexityProfile ComplexityProfile.cpp -std=c++17 -O2
```

```bash
./ComplexityProfile -d db.txt -s meta.txt -k 3 -a 0.1 -t 20
```
- Run complexity.py to generate the complexity profile graph

---

