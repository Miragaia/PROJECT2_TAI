#!/usr/bin/env python3

import subprocess
import json
import os
import argparse
from datetime import datetime
import statistics

def run_metaclass(db_file, sample_file, k, alpha, top_n):
    """Run the MetaClass binary with the given parameters and capture its output"""
    cmd = ["./MetaClass", "-d", db_file, "-s", sample_file, 
           "-k", str(k), "-a", str(alpha), "-t", str(top_n)]
    
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running MetaClass: {e}")
        print(f"Error output: {e.stderr}")
        return None

def parse_output(output):
    """Parse the standard output from MetaClass to extract the results"""
    if not output:
        return None
    
    lines = output.strip().split("\n")
    results = []
    
    # Find where the results table starts
    start_idx = -1
    for i, line in enumerate(lines):
        if line.startswith("Rank\tNRC Value\tSequence ID"):
            start_idx = i + 2  # Skip the header line and separator
            break
    
    if start_idx == -1 or start_idx >= len(lines):
        return None
    
    # Parse the results table
    for i in range(start_idx, len(lines)):
        parts = lines[i].split("\t")
        if len(parts) < 3:
            continue
        
        results.append({
            "rank": int(parts[0]),
            "nrc": float(parts[1]),
            "sequence_id": parts[2]
        })
    
    # Extract all NRC values by parsing the full output
    all_nrc_values = []
    for line in lines:
        if " - NRC: " in line:
            try:
                nrc_value = float(line.split(" - NRC: ")[1])
                all_nrc_values.append(nrc_value)
            except (ValueError, IndexError):
                pass
    
    return {
        "top_results": results,
        "all_nrc_values": all_nrc_values,
        "mean_nrc": statistics.mean(all_nrc_values) if all_nrc_values else None,
        "min_nrc": min(all_nrc_values) if all_nrc_values else None,
        "max_nrc": max(all_nrc_values) if all_nrc_values else None
    }

def main():
    parser = argparse.ArgumentParser(description="Run MetaClass with different parameters")
    parser.add_argument("-d", "--db_file", required=True, help="Database file path")
    parser.add_argument("-s", "--sample_file", required=True, help="Sample file path")
    parser.add_argument("-t", "--top_n", type=int, default=10, help="Number of top results to show")
    parser.add_argument("-o", "--output", default="metaclass_results.json", help="Output JSON file")
    parser.add_argument("--k_values", type=str, default="2,3,4,5,6", help="Comma-separated k values")
    parser.add_argument("--alpha_values", type=str, default="0.1,0.5,1.0,2.0", help="Comma-separated alpha values")
    
    args = parser.parse_args()
    
    # Parse k and alpha values
    k_values = [int(k) for k in args.k_values.split(",")]
    alpha_values = [float(a) for a in args.alpha_values.split(",")]
    
    # Initialize results dictionary
    all_results = {
        "metadata": {
            "db_file": args.db_file,
            "sample_file": args.sample_file,
            "top_n": args.top_n,
            "timestamp": datetime.now().isoformat(),
        },
        "parameters": {
            "k_values": k_values,
            "alpha_values": alpha_values
        },
        "results": {},
        "summary": {
            "mean_nrc_by_params": {}
        }
    }
    
    # Run for each combination of parameters
    for k in k_values:
        all_results["results"][f"k={k}"] = {}
        all_results["summary"]["mean_nrc_by_params"][f"k={k}"] = {}
        
        for alpha in alpha_values:
            print(f"\n--- Running with k={k}, alpha={alpha} ---")
            output = run_metaclass(args.db_file, args.sample_file, k, alpha, args.top_n)
            
            if output:
                parsed_results = parse_output(output)
                if parsed_results:
                    # Store the top results
                    all_results["results"][f"k={k}"][f"alpha={alpha}"] = parsed_results["top_results"]
                    
                    # Store statistics in the summary
                    all_results["summary"]["mean_nrc_by_params"][f"k={k}"][f"alpha={alpha}"] = {
                        "mean": parsed_results["mean_nrc"],
                        "min": parsed_results["min_nrc"],
                        "max": parsed_results["max_nrc"]
                    }
                    
                    print(f"Mean NRC: {parsed_results['mean_nrc']:.6f}")
                else:
                    print("Failed to parse output")
                    all_results["results"][f"k={k}"][f"alpha={alpha}"] = {"error": "Failed to parse output"}
            else:
                print("Failed to run MetaClass")
                all_results["results"][f"k={k}"][f"alpha={alpha}"] = {"error": "Failed to run MetaClass"}
    
    # Generate a summary table of mean NRC values for quick comparison
    summary_table = []
    header = ["k / alpha"] + [str(alpha) for alpha in alpha_values]
    summary_table.append(header)
    
    for k in k_values:
        row = [str(k)]
        for alpha in alpha_values:
            mean_value = all_results["summary"]["mean_nrc_by_params"][f"k={k}"].get(f"alpha={alpha}", {}).get("mean", "N/A")
            if mean_value != "N/A":
                mean_value = f"{mean_value:.6f}"
            row.append(mean_value)
        summary_table.append(row)
    
    all_results["summary"]["mean_nrc_table"] = summary_table
    
    # Save results to JSON file
    with open(args.output, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print summary table to console
    print("\nSummary of Mean NRC Values:")
    for row in summary_table:
        print("\t".join(row))
    
    print(f"\nResults saved to {args.output}")

if __name__ == "__main__":
    main()