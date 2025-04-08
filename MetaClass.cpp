#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <cmath>
#include <iomanip>
#include <filesystem> 

#include "load_database.h"
#include "fcm.h"
#include "load_sample.h"

using namespace std;

int main(int argc, char *argv[]) {
    if (argc < 7) {
        cerr << "Usage: " << argv[0] << " -d <db_file> -s <sample_file> -k <order> -a <alpha> -t <top_n> [-c <matrix_output_file>]\n";
        return 1;
    }

    string db_filename, sample_filename, compareMatrixFile;
    int k = 0, top_n = 0;
    double alpha = 0.0;
    bool generate_profile = false;

    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];
        if (arg == "-d" && i + 1 < argc) db_filename = argv[++i];
        else if (arg == "-s" && i + 1 < argc) sample_filename = argv[++i];
        else if (arg == "-k" && i + 1 < argc) k = stoi(argv[++i]);
        else if (arg == "-a" && i + 1 < argc) alpha = stod(argv[++i]);
        else if (arg == "-t" && i + 1 < argc) top_n = stoi(argv[++i]);
        else if (arg == "-c" && i + 1 < argc) compareMatrixFile = argv[++i];
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

    // Optional: compare top N sequences with each other
    if (!compareMatrixFile.empty()) {
        ofstream out(compareMatrixFile);
        if (!out) {
            cerr << "Error: Cannot open file " << compareMatrixFile << " for writing.\n";
            return 1;
        }

        // CSV header
        out << "ID";
        for (const auto& entry : top_sequences) {
            out << ",\"" << entry.first << "\"";
        }
        out << "\n";

        for (size_t i = 0; i < top_sequences.size(); ++i) {
            const auto& ref_id = top_sequences[i].first;
            const auto& ref_seq = top_sequences[i].second;

            out << "\"" << ref_id << "\"";

            // Train model on reference sequence
            FCM ref_model(k, alpha);
            ref_model.train(ref_seq);

            for (size_t j = 0; j < top_sequences.size(); ++j) {
                const auto& target_seq = top_sequences[j].second;
                double nrc = ref_model.compute_nrc(target_seq);
                out << "," << fixed << setprecision(6) << nrc;
            }
            out << "\n";
        }

        out.close();
        cout << "\nNRC comparison matrix saved to: " << compareMatrixFile << endl;
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
