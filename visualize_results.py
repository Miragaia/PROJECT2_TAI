#!/usr/bin/env python3

import json
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

def create_nrc_dataframe(data, value_type="mean"):
    """Create a DataFrame from the JSON results for heatmap visualization"""
    k_values = [int(k.split('=')[1]) for k in data["summary"]["mean_nrc_by_params"].keys()]
    alpha_values = []
    
    # Extract alpha values from the first k entry
    first_k = list(data["summary"]["mean_nrc_by_params"].keys())[0]
    alpha_values = [float(a.split('=')[1]) for a in data["summary"]["mean_nrc_by_params"][first_k].keys()]
    
    # Sort the values
    k_values.sort()
    alpha_values.sort()
    
    # Create empty dataframe with explicit float dtype
    df = pd.DataFrame(index=k_values, columns=alpha_values, dtype=float)
    df.index.name = 'k'
    df.columns.name = 'alpha'
    
    # Fill the dataframe with values
    for k in k_values:
        k_key = f"k={k}"
        for alpha in alpha_values:
            alpha_key = f"alpha={alpha}"
            try:
                value = data["summary"]["mean_nrc_by_params"][k_key][alpha_key][value_type]
                # Ensure value is a float or convert to NaN
                df.at[k, alpha] = float(value) if value is not None else np.nan
            except (KeyError, TypeError, ValueError):
                df.at[k, alpha] = np.nan
    
    return df

def plot_heatmap(df, title, filename, cmap="viridis_r", fmt=".4f", annot=True):
    """Create a heatmap visualization from a DataFrame"""
    plt.figure(figsize=(10, 8))
    
    # Debug info
    print(f"Dataframe shape: {df.shape}")
    print(f"Dataframe dtypes: {df.dtypes}")
    print(f"Any NaN values: {df.isna().any().any()}")
    
    # Check for any non-numeric values that might cause issues
    if np.any(pd.isna(df)) or np.any(np.isinf(df)):
        print("Warning: DataFrame contains NaN or Inf values.")
        
    # Convert any remaining object dtypes to float
    df = df.astype(float)
    
    # Create the heatmap
    ax = sns.heatmap(df, annot=annot, fmt=fmt, cmap=cmap, 
                     linewidths=0.5, cbar_kws={'label': 'NRC Value'})
    
    # Add labels and title
    plt.xlabel('Alpha (Smoothing Parameter)')
    plt.ylabel('k (Context Length)')
    plt.title(title, fontsize=14)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    
    print(f"Saved heatmap to {filename}")

def plot_min_values(df_mean, df_min, output_prefix):
    """Create a combination plot showing minimum NRC values with markers"""
    plt.figure(figsize=(12, 9))
    
    # Create a custom diverging colormap
    cmap = sns.color_palette("viridis_r", as_cmap=True)
    
    # Plot mean NRC values as the base heatmap
    ax = sns.heatmap(df_mean, annot=True, fmt=".4f", cmap=cmap, 
                     linewidths=0.5, cbar_kws={'label': 'Mean NRC Value'})
    
    # Find the minimum NRC value and its position
    min_value = df_min.min().min()
    min_pos = np.where(df_min.values == min_value)
    if len(min_pos[0]) > 0:
        min_k = df_min.index[min_pos[0][0]]
        min_alpha = df_min.columns[min_pos[1][0]]
        
        # Add a marker for the minimum value
        plt.plot(min_pos[1][0] + 0.5, min_pos[0][0] + 0.5, 'r*', markersize=20)
        
        plt.title(f"Mean NRC Values with Best Performance Marker\nBest: k={min_k}, α={min_alpha}, Min NRC={min_value:.6f}", 
                  fontsize=14)
    else:
        plt.title("Mean NRC Values with Best Performance Marker", fontsize=14)
    
    plt.xlabel('Alpha (Smoothing Parameter)')
    plt.ylabel('k (Context Length)')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_best_performance.png", dpi=300)
    plt.close()
    
    print(f"Saved best performance visualization to {output_prefix}_best_performance.png")

def plot_parameter_impact(df_mean, output_prefix):
    """Create line plots showing the impact of each parameter separately"""
    plt.figure(figsize=(15, 6))
    
    # Create a subplot for k impact
    plt.subplot(1, 2, 1)
    for alpha in df_mean.columns:
        plt.plot(df_mean.index, df_mean[alpha], marker='o', label=f'α={alpha}')
    
    plt.xlabel('k (Context Length)')
    plt.ylabel('Mean NRC Value')
    plt.title('Impact of k on NRC (Lower is Better)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    # Create a subplot for alpha impact
    plt.subplot(1, 2, 2)
    for k in df_mean.index:
        plt.plot(df_mean.columns, df_mean.loc[k], marker='o', label=f'k={k}')
    
    plt.xlabel('Alpha (Smoothing Parameter)')
    plt.ylabel('Mean NRC Value')
    plt.title('Impact of Alpha on NRC (Lower is Better)')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_parameter_impact.png", dpi=300)
    plt.close()
    
    print(f"Saved parameter impact plots to {output_prefix}_parameter_impact.png")

def plot_3d_surface(df_mean, output_prefix):
    """Create a 3D surface plot for better visualization of the parameter space"""
    try:
        from mpl_toolkits.mplot3d import Axes3D  # Import for 3D plotting
        
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        
        # Create meshgrid from the dataframe indices and columns
        X, Y = np.meshgrid(df_mean.columns.astype(float), df_mean.index.astype(float))
        Z = df_mean.values
        
        # Plot the surface
        surf = ax.plot_surface(X, Y, Z, cmap='viridis_r', linewidth=0, antialiased=True, alpha=0.8)
        
        # Add colorbar
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='Mean NRC Value')
        
        # Set labels
        ax.set_xlabel('Alpha (Smoothing Parameter)')
        ax.set_ylabel('k (Context Length)')
        ax.set_zlabel('Mean NRC Value')
        ax.set_title('3D Surface Plot of NRC Values (Lower is Better)')
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(f"{output_prefix}_3d_surface.png", dpi=300)
        plt.close()
        
        print(f"Saved 3D surface plot to {output_prefix}_3d_surface.png")
    except Exception as e:
        print(f"Warning: Could not create 3D surface plot: {e}")

def print_json_structure(data, output_prefix):
    """Print structure of JSON file to help debug issues"""
    try:
        # Check if summary exists
        if "summary" not in data:
            print("ERROR: No 'summary' key found in JSON file!")
            return
            
        if "mean_nrc_by_params" not in data["summary"]:
            print("ERROR: No 'mean_nrc_by_params' key found in JSON summary!")
            return
            
        # Write structure to file
        with open(f"{output_prefix}_structure.txt", "w") as f:
            f.write("JSON Structure:\n")
            f.write("=============\n\n")
            
            # List all keys at the top level
            f.write("Top level keys: " + ", ".join(data.keys()) + "\n\n")
            
            # Summary section
            f.write("Summary keys: " + ", ".join(data["summary"].keys()) + "\n\n")
            
            # Examine the structure of mean_nrc_by_params
            f.write("Structure of mean_nrc_by_params:\n")
            for k_key in data["summary"]["mean_nrc_by_params"]:
                f.write(f"  {k_key}:\n")
                for alpha_key in data["summary"]["mean_nrc_by_params"][k_key]:
                    f.write(f"    {alpha_key}: {data['summary']['mean_nrc_by_params'][k_key][alpha_key]}\n")
            
        print(f"JSON structure written to {output_prefix}_structure.txt for debugging")
    except Exception as e:
        print(f"Error examining JSON structure: {e}")

def main():
    parser = argparse.ArgumentParser(description="Visualize MetaClass parameter sweeps from JSON results")
    parser.add_argument("json_file", help="JSON results file from parameter sweep")
    parser.add_argument("-o", "--output", default="metaclass_viz", help="Output prefix for visualization files")
    parser.add_argument("-d", "--output-dir", default=".", help="Directory to save visualization files")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    import os
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
            print(f"Created output directory: {args.output_dir}")
        except Exception as e:
            print(f"Error creating output directory: {e}")
            return
    
    # Load JSON data
    print(f"Loading JSON data from {args.json_file}...")
    try:
        with open(args.json_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON file: {e}")
        return
    except Exception as e:
        print(f"Error opening or reading JSON file: {e}")
        return
    
    # Print JSON structure for debugging
    if args.debug:
        print_json_structure(data, os.path.join(args.output_dir, args.output))
    
    print("Generating visualizations...")
    
    try:
        # Create dataframes for different metrics
        df_mean = create_nrc_dataframe(data, "mean")
        df_min = create_nrc_dataframe(data, "min")
        df_max = create_nrc_dataframe(data, "max")
        
        if args.debug:
            print("Mean NRC DataFrame:")
            print(df_mean)
        
        # Full output path with directory
        output_path = os.path.join(args.output_dir, args.output)
        
        # Create heatmaps
        plot_heatmap(df_mean, "Mean NRC Values by k and Alpha (Lower is Better)", 
                     f"{output_path}_mean.png", cmap="viridis_r")
        plot_heatmap(df_min, "Minimum NRC Values by k and Alpha (Lower is Better)", 
                     f"{output_path}_min.png", cmap="viridis_r")
        plot_heatmap(df_max, "Maximum NRC Values by k and Alpha (Lower is Better)", 
                     f"{output_path}_max.png", cmap="viridis_r")
        
        # Range of NRC values (max - min)
        df_range = df_max - df_min
        plot_heatmap(df_range, "Range of NRC Values by k and Alpha", 
                     f"{output_path}_range.png", cmap="YlOrRd")
        
        # Plot best parameter combination
        plot_min_values(df_mean, df_min, output_path)
        
        # Plot parameter impact
        plot_parameter_impact(df_mean, output_path)
        
        # 3D surface plot
        plot_3d_surface(df_mean, output_path)
        
        print(f"All visualizations saved in directory: {args.output_dir}")
        print(f"Files prefix: {args.output}")
        
    except Exception as e:
        import traceback
        print(f"Error generating visualizations: {e}")
        if args.debug:
            print(traceback.format_exc())

if __name__ == "__main__":
    main()