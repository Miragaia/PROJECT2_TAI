#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <utility>

using namespace std;

// Function to load the metagenomic sample
string load_sample(const string &sample_filename) {
    ifstream file(sample_filename);
    if (!file) {
        cerr << "Error opening sample file " << sample_filename << "\n";
        exit(1);
    }
    
    string sample_text;
    string line;
    while (getline(file, line)) {
        sample_text += line;
    }
    file.close();
    
    return sample_text;
}