#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <sstream>
#include <filesystem> 

#include "load_database.h"
#include "fcm.h"
#include "load_sample.h"

using namespace std;

// Function to write matrix data to CSV for external visualization
void write_similarity_matrix_to_csv(const vector<pair<string, string>>& sequences, 
    const vector<vector<double>>& matrix, 
    const string& output_file) {
    
    // Create directory if it doesn't exist
    string directory = "similarity_matrix";
    if (!filesystem::exists(directory)) {
        filesystem::create_directory(directory);
    }
    
    // Combine directory and filename
    string full_path = directory + "/" + output_file;
    
    ofstream outfile(full_path);
    if (!outfile) {
        cerr << "Error: Could not open file " << full_path << " for writing." << endl;
        return;
    }

    // Write header row with sequence IDs
    outfile << "Sequence";
    for (const auto& seq : sequences) {
        // Quote the sequence ID to handle commas and other special characters
        outfile << ",\"" << seq.first << "\"";
    }
    outfile << endl;

    // Write matrix rows
    for (size_t i = 0; i < sequences.size(); ++i) {
        // Quote the sequence ID
        outfile << "\"" << sequences[i].first << "\"";
        for (size_t j = 0; j < sequences.size(); ++j) {
            outfile << "," << fixed << setprecision(6) << matrix[i][j];
        }
        outfile << endl;
    }

    outfile.close();
    cout << "Similarity matrix saved to " << full_path << endl;
}

// Function to calculate similarity matrix for top sequences
void generate_similarity_matrix(const vector<pair<string, string>>& sequences, 
    int k, double alpha, const string& output_file) {
    int limit = sequences.size();
    cout << "Generating similarity matrix for " << limit << " sequences..." << endl;

    // Pre-train FCM models for each sequence to avoid redundant training
    vector<FCM> trained_models;
    for (const auto& seq_pair : sequences) {
        FCM model(k, alpha);
        model.train(seq_pair.second);
        trained_models.push_back(model);
    }

    // Initialize matrix with zeros
    vector<vector<double>> similarity_matrix(limit, vector<double>(limit, 0.0));

    // Calculate NRC for each pair of sequences using pre-trained models
    for (int i = 0; i < limit; ++i) {
        cout << "Processing sequence " << i+1 << "/" << limit << ": " << sequences[i].first << endl;

        // Set diagonal element using self-comparison
        similarity_matrix[i][i] = trained_models[i].compute_nrc(sequences[i].second);

        for (int j = i+1; j < limit; ++j) {
            // Use trained model i to compute NRC for sequence j
            similarity_matrix[i][j] = trained_models[i].compute_nrc(sequences[j].second);

            // Use trained model j to compute NRC for sequence i
            similarity_matrix[j][i] = trained_models[j].compute_nrc(sequences[i].second);
        }
    }

    // Write matrix to CSV
    write_similarity_matrix_to_csv(sequences, similarity_matrix, output_file);
}

// Function to calculate NRC between sequences using the FCM model
double calculate_nrc(const string& seq1, const string& seq2, int k, double alpha) {
    FCM model(k, alpha);
    model.train(seq1);
    return model.compute_nrc(seq2);
}

int main(int argc, char *argv[]) {
    if (argc < 7) {
        cerr << "Usage: " << argv[0] << " -d <db_file> -s <sample_file> -k <order> -a <alpha> -t <top_n> [-c <matrix_output_file>]\n";
        return 1;
    }

    string db_filename, sample_filename, matrix_output = "similarity_matrix.csv";
    int k = 0, top_n = 0;
    double alpha = 0.0;
    bool generate_matrix = false;
    bool generate_profile = false;

    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "-d" && i + 1 < argc) db_filename = argv[++i];
        else if (arg == "-s" && i + 1 < argc) sample_filename = argv[++i];
        else if (arg == "-k" && i + 1 < argc) k = stoi(argv[++i]);
        else if (arg == "-a" && i + 1 < argc) alpha = stod(argv[++i]);
        else if (arg == "-t" && i + 1 < argc) top_n = stoi(argv[++i]);
        else if (arg == "-c" && i + 1 < argc) {
            matrix_output = argv[++i];
            generate_matrix = true;
        }
        else if (arg == "-cp") generate_profile = true;
        else {
            cerr << "Unknown or incomplete parameter: " << arg << endl;
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
    unordered_map<string, string> id_to_seq;

    for (const auto &entry : db_sequences) {
        string id = entry.first;
        string seq = entry.second;

        cout << "Processing: " << id << " (" << seq.length() << " bp)";

        double nrc = model.compute_nrc(seq);
        nrc_results.emplace_back(nrc, id);
        id_to_seq[id] = seq;

        cout << " - NRC: " << fixed << setprecision(6) << nrc << endl;
    }

    // Sort by NRC (ascending, lower is better)
    sort(nrc_results.begin(), nrc_results.end());

    // Output top N
    cout << "\nTop " << top_n << " similar sequences based on NRC:\n";
    cout << "Rank\tNRC Value\tSequence ID\n";
    cout << "----------------------------------------\n";

    int limit = min(top_n, (int)nrc_results.size());
    vector<pair<string, string>> top_sequences;
    for (int i = 0; i < limit; ++i) {
        cout << i + 1 << "\t" << fixed << setprecision(6) << nrc_results[i].first 
             << "\t" << nrc_results[i].second << endl;
        top_sequences.emplace_back(nrc_results[i].second, id_to_seq[nrc_results[i].second]);
    }

    // Generate similarity matrix if requested
    if (generate_matrix) {
        generate_similarity_matrix(top_sequences, k, alpha, matrix_output);
    }

    if (generate_profile) {
        string output_dir = "complexity_profile";
        if (!filesystem::exists(output_dir)) {
            filesystem::create_directory(output_dir);
        }

        for (const auto &entry : db_sequences) {
            string id = entry.first;
            string seq = entry.second;

            cout << "Processing: " << id << " (" << seq.length() << " bp)" << endl;

            vector<double> complexity_values = model.compute_complexity_profile(seq);

            string filename = "complexity_" + id + ".csv";
            replace(filename.begin(), filename.end(), ' ', '_');
            replace(filename.begin(), filename.end(), '/', '_');

            string filepath = output_dir + "/" + filename;

            ofstream profile_file(filepath);
            profile_file << "Position,Complexity,SequenceID\n";

            for (size_t i = 0; i < complexity_values.size(); i++) {
                profile_file << i << "," << complexity_values[i] << ",\"" << id << "\"\n";
            }

            profile_file.close();
        }

        cout << "\nComplexity profiles saved to '" << output_dir << "' directory.\n";
    }

    return 0;
}