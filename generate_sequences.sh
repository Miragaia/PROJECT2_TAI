#!/bin/bash

# Check if number of iterations is provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 <number_of_iterations>"
  exit 1
fi

# Number of iterations
iterations=$1

# Output file
output_file="random_dna_sequences.txt"

# Clear output file if it exists
> $output_file

# Generate sequences
for i in $(seq 1 $iterations); do
  # Generate a random seed
  random_seed=$RANDOM
  
  # Generate a random length between 5000-20000
  random_length=$(( RANDOM % 15001 + 5000 ))
  
  # Add header to output file
  echo "@$i" >> $output_file
  
  # Generate DNA sequence with random seed and length
  ./gto_genomic_gen_random_dna -s $random_seed -n $random_length >> $output_file
  
  # Add an empty line after each sequence
  echo "" >> $output_file
  
  echo "Generated sequence $i with length $random_length and seed $random_seed"
done

echo "Generated $iterations DNA sequences in $output_file"