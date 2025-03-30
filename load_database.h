#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <utility>

using namespace std;

vector<pair<string, string>> load_database(const string &db_filename) {
    vector<pair<string, string>> sequences; // Pair of (identifier, sequence)
    ifstream file(db_filename);
    if (!file) {
        cerr << "Error opening database file " << db_filename << "\n";
        exit(1);
    }

    string line, current_id, current_seq;
    while (getline(file, line)) {
        if (line.empty()) continue;
        if (line[0] == '@') {
            if (!current_id.empty()) {
                sequences.emplace_back(current_id, current_seq);
            }
            current_id = line.substr(1); // Remove '@'
            current_seq.clear();
        } else {
            current_seq += line;
        }
    }
    if (!current_id.empty()) {
        sequences.emplace_back(current_id, current_seq);
    }
    file.close();
    return sequences;
}