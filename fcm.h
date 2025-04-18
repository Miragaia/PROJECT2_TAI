#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <cmath>

using namespace std;

class FCM {
    public:
        int k;
        double alpha;
        std::unordered_map<std::string, std::unordered_map<char, int>> context_counts;
        std::unordered_map<std::string, int> total_counts;
        std::unordered_set<char> alphabet;
    
        FCM(int k, double alpha) : k(k), alpha(alpha) {}
    
        void train(const std::string &text) {
            // Clear any existing model data
            context_counts.clear();
            total_counts.clear();
            alphabet.clear();
            
            // Train the model on the text
            for (size_t i = k; i < text.size(); ++i) {
                std::string context = text.substr(i - k, k);
                char symbol = text[i];
                context_counts[context][symbol]++;
                total_counts[context]++;
                alphabet.insert(symbol);
            }
            
            cout << "Trained model with context length k=" << k << endl;
            cout << "Alphabet size: " << alphabet.size() << endl;
            cout << "Unique contexts: " << context_counts.size() << endl;
        }
    
        // Compute bits needed to compress a sequence given the trained model
        double compute_compression_bits(const std::string &x) {
            double total_bits = 0.0;
            size_t alphabet_size = alphabet.size();
            if (alphabet_size == 0) alphabet_size = 4; // DNA sequences have 4 symbols (A,C,G,T)
            double smoothing_factor = alpha * alphabet_size;
    
            for (size_t i = k; i < x.size(); ++i) {
                std::string context = x.substr(i - k, k);
                char symbol = x[i];
    
                // Get the count of the symbol in the context
                int count = context_counts[context][symbol];

                // Get the total count of symbols in the context
                int total = total_counts[context];
                
                double prob = static_cast<double>(count + smoothing_factor) /
                              (total + smoothing_factor * alphabet_size);
                              
                total_bits += -std::log2(prob); // Bits = -log2(probability)
            }
            
            return total_bits;
        }
    
        // Compute NRC for a sequence given the trained model
        double compute_nrc(const std::string &x) {
            if (x.length() <= k) {
                // Return a high value for sequences shorter than k+1
                return 1.0; // Maximum NRC is 1.0
            }
            
            double bits = compute_compression_bits(x);
            // According to the formula, NRC = C(x||y) / (|x| * log2(A))
            // For DNA, log2(A) = log2(4) = 2
            // Also, we only compress x[k:] since we need context
            double nrc = bits / (2.0 * (x.length() - k));
            
            return nrc;
        }

        //Computes complexity per base
        std::vector<double> compute_complexity_profile(const std::string &seq) {
            std::vector<double> profile(seq.size(), 0.0);
            size_t alphabet_size = alphabet.size();
            if (alphabet_size == 0) alphabet_size = 4; 
            double smoothing_factor = alpha * alphabet_size;

            for (size_t i = k; i < seq.size(); ++i) {
                std::string context = seq.substr(i - k, k);
                char symbol = seq[i];

                int count = context_counts[context][symbol];
                int total = total_counts[context];
                
                double prob = static_cast<double>(count + smoothing_factor) /
                              (total + smoothing_factor * alphabet_size);
                
                profile[i] = -std::log2(prob);  // Store complexity per base
            }
            
            return profile;
        }
    };