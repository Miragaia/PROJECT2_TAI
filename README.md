# PROJECT2_TAI
First Year - MEI - 2nd Semester Class (Universidade de Aveiro) - Algorithmic Theory of Information 

## How this works:

1. Trains a finite-context model (FCM) on meta.txt.
2. Freezes model counts (i.e., no more learning after training).
3. Reads db.txt, extracting DNA sequences and their names.
4. Computes the compression bits required for each reference sequence.
5. Computes NRC scores and sorts them in ascending order (lower NRC = higher similarity).
6. Prints the top 20 matches.

## How to compile and run:
```bash
g++ -o MetaClass MetaClass.cpp -std=c++17 -O2

./MetaClass -d db.txt -s meta.txt -k 10 -a 0.1 -t 20
```