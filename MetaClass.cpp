#include <iostream>
#include <fstream>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <cmath>
#include <iomanip>
#include <algorithm>

using namespace std;

class FCM {
public:
    int k;
    double alpha;
    unordered_map<string, unordered_map<char, int>> context_counts;
    unordered_map<string, int> total_counts;
    unordered_set<char> alphabet;

    FCM(int k, double alpha) : k(k), alpha(alpha) {}

    void train(const string &text) {
        for (size_t i = k; i < text.size(); ++i) {
            string context = text.substr(i - k, k);
            char symbol = text[i];

            // Ensure context exists before incrementing
            context_counts[context][symbol]++;
            total_counts[context]++;
            alphabet.insert(symbol);
        }
    }

    double compute_bits(const string &sequence) {
        double total_bits = 0.0;
        size_t alphabet_size = max(alphabet.size(), (size_t)4);  // DNA sequences: {A, C, G, T}
        double smoothing_factor = alpha * alphabet_size;
        double default_prob = 1.0 / (alphabet_size * 10);  // Assign a small probability for unseen contexts
    
        for (size_t i = k; i < sequence.size(); ++i) {
            string context = sequence.substr(i - k, k);
            char symbol = sequence[i];
    
            // Check if the context exists in the trained model
            if (context_counts.find(context) == context_counts.end()) {
                // Context was not seen in training → Apply a small probability
                total_bits += -log2(default_prob);
                continue;
            }
    
            // Apply smoothing
            int count = context_counts[context][symbol] + alpha;
            int total = total_counts[context] + smoothing_factor;
    
            if (total <= 0) continue; // Avoid division by zero
    
            double prob = (double)count / total;
    
            // Prevent log2(0) errors
            if (prob > 0) {
                total_bits += -log2(prob);
            } else {
                cerr << "Warning: Encountered zero probability for context: " << context << " and symbol: " << symbol << endl;
            }
        }
    
        return total_bits;
    }    
};

// Function to read the metagenomic sample (y)
string read_metagenomic_sample(const string &filename) {
    ifstream file(filename);
    if (!file) {
        cerr << "Error opening file " << filename << endl;
        exit(1);
    }
    string sample((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    file.close();
    return sample;
}

// Function to read the reference database (xi)
vector<pair<string, string>> read_reference_database(const string &filename) {
    ifstream file(filename);
    if (!file) {
        cerr << "Error opening file " << filename << endl;
        exit(1);
    }
    vector<pair<string, string>> sequences;
    string line, name, sequence;

    while (getline(file, line)) {
        if (line.empty()) continue;
        if (line[0] == '@') {  // Name identifier
            if (!name.empty()) {
                sequences.emplace_back(name, sequence);
            }
            name = line.substr(1); // Remove '@'
            sequence.clear();
        } else {
            sequence += line; // Append sequence data
        }
    }
    if (!name.empty()) { 
        sequences.emplace_back(name, sequence);
    }

    file.close();
    return sequences;
}

// Compute NRC for a given sequence
double compute_nrc(const string &sequence, FCM &model) {
    if (sequence.empty()) {
        cerr << "Warning: Encountered an empty sequence, skipping NRC computation.\n";
        return NAN;
    }

    double bits = model.compute_bits(sequence);

    // Avoid division by zero
    if (sequence.size() == 0) return NAN;

    double nrc = bits / (2 * sequence.size());

    // Debugging Output
    cout << "Sequence Length: " << sequence.size() << " | Bits: " << bits << " | NRC: " << nrc << endl;

    return nrc;
}

int main(int argc, char *argv[]) {
    if (argc < 6) {
        cerr << "Usage: ./MetaClass -d <db.txt> -s <meta.txt> -k <order> -a <alpha> -t <top_N>\n";
        return 1;
    }

    string db_file = argv[2];
    string meta_file = argv[4];
    int k = stoi(argv[6]);
    double alpha = stod(argv[8]);
    int top_N = stoi(argv[10]);

    // Step 1: Train model on metagenomic sample
    cout << "Training model on metagenomic sample..." << endl;
    string metagenomic_sample = read_metagenomic_sample(meta_file);
    FCM model(k, alpha);
    model.train(metagenomic_sample);

    // Step 2: Compute NRC scores for reference database
    cout << "Computing NRC scores..." << endl;
    vector<pair<string, double>> nrc_scores;
    vector<pair<string, string>> reference_sequences = read_reference_database(db_file);

    for (const auto &[name, sequence] : reference_sequences) {
        double nrc = compute_nrc(sequence, model);

        // Skip NaN or infinite values
        if (!isnan(nrc) && isfinite(nrc)) {
            nrc_scores.emplace_back(name, nrc);
        } else {
            cerr << "Skipping sequence " << name << " due to invalid NRC value." << endl;
        }
    }

    // Step 3: Sort and print the top N matches
    sort(nrc_scores.begin(), nrc_scores.end(), [](const auto &a, const auto &b) {
        return a.second < b.second; // Lower NRC means higher similarity
    });

    cout << "Top " << top_N << " matches based on NRC:\n";
    for (int i = 0; i < min(top_N, (int)nrc_scores.size()); ++i) {
        cout << i + 1 << ". " << nrc_scores[i].first << " - NRC: " << fixed << setprecision(6) << nrc_scores[i].second << endl;
    }

    return 0;
}
