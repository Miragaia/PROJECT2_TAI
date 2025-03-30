#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cmath>
#include <iomanip>

#include "load_database.h"
#include "fcm.h"
#include "load_sample.h"

using namespace std;

int main(int argc, char *argv[]) {
    if (argc < 7) {
        cerr << "Usage: " << argv[0] << " -d <db_file> -s <sample_file> -k <order> -a <alpha> -t <top_n>\n";
        return 1;
    }

    string db_filename, sample_filename;
    int k = 0, top_n = 0;
    double alpha = 0.0;

    for (int i = 1; i < argc; i += 2) {
        if (i + 1 >= argc) {
            cerr << "Missing value for parameter " << argv[i] << endl;
            return 1;
        }
        
        string arg = argv[i];
        if (arg == "-d") db_filename = argv[i + 1];
        else if (arg == "-s") sample_filename = argv[i + 1];
        else if (arg == "-k") k = stoi(argv[i + 1]);
        else if (arg == "-a") alpha = stod(argv[i + 1]);
        else if (arg == "-t") top_n = stoi(argv[i + 1]);
        else {
            cerr << "Unknown parameter: " << arg << endl;
            return 1;
        }
    }

    // Validate parameters
    if (db_filename.empty() || sample_filename.empty() || k <= 0 || alpha <= 0 || top_n <= 0) {
        cerr << "Invalid parameters" << endl;
        return 1;
    }

    cout << "Loading metagenomic sample from " << sample_filename << "..." << endl;
    string meta_text = load_sample(sample_filename);
    cout << "Sample loaded: " << meta_text.length() << " base pairs" << endl;

    // Train model on meta.txt (the sample)
    cout << "Training model on metagenomic sample..." << endl;
    FCM model(k, alpha);
    model.train(meta_text);
    cout << "Model training complete." << endl;

    // Load database sequences
    cout << "Loading reference database from " << db_filename << "..." << endl;
    vector<pair<string, string>> db_sequences = load_database(db_filename);
    cout << "Database loaded: " << db_sequences.size() << " sequences" << endl;

    // Compute NRC for each sequence in the database
    cout << "Computing NRC for database sequences..." << endl;
    vector<pair<double, string>> nrc_results; // Pair of (NRC, identifier)
    
    for (const auto &entry : db_sequences) {
        string id = entry.first;
        string seq = entry.second;
        
        cout << "Processing: " << id << " (" << seq.length() << " bp)";
        
        double nrc = model.compute_nrc(seq);
        nrc_results.emplace_back(nrc, id);
        
        cout << " - NRC: " << fixed << setprecision(6) << nrc << endl;
    }

    // Sort by NRC (ascending, lower is better)
    sort(nrc_results.begin(), nrc_results.end());

    // Output top N
    cout << "\nTop " << top_n << " similar sequences based on NRC:\n";
    cout << "Rank\tNRC Value\tSequence ID\n";
    cout << "----------------------------------------\n";
    
    int limit = min(top_n, (int)nrc_results.size());
    for (int i = 0; i < limit; ++i) {
        cout << i + 1 << "\t" << fixed << setprecision(6) << nrc_results[i].first 
             << "\t" << nrc_results[i].second << endl;
    }

    return 0;
}