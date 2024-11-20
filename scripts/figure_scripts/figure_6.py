import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Get the directory of the script being run
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '../../data/all_subjects_tSNR_data.csv')

# Load the data that was saved previously
df_all_subjects = pd.read_csv(data_path)

# Define a function to compute mean and std
def compute_bounds(df, value_column):
    summary = (
        df.groupby(['Spinal Level', 'Condition'])
        .agg(mean=(value_column, 'mean'), std=(value_column, 'std'))
        .reset_index()
    )
    summary['lower'] = summary['mean'] - summary['std']
    summary['upper'] = summary['mean'] + summary['std']
    return summary

# Compute bounds for each plot
wa_summary = compute_bounds(df_all_subjects, 'WA()')
improvement_summary = compute_bounds(df_all_subjects, '% Improvement')
signal_loss_summary = compute_bounds(df_all_subjects, 'Predicted signal Loss')

# Define a color palette and markers
palette = {'Baseline': 'blue', 'DynShim': 'green', 'SigRec': 'red'}
markers = {'Baseline': 'o', 'DynShim': 'X', 'SigRec': 's'}
styles = {'Baseline': '-', 'DynShim': '-', 'SigRec': '-'}

# Set up the figure and style
f, axes = plt.subplots(1, 3, figsize=(15, 3.2))
sns.set(style="whitegrid")

# Function to plot data with line tags
def plot_with_tags(ax, data, title):
    for condition in data['Condition'].unique():
        subset = data[data['Condition'] == condition]
        color = palette[condition]
        marker = markers[condition]
        linestyle = styles[condition]
        
        # Plot the mean line with marker and linestyle
        ax.plot(
            subset['Spinal Level'], subset['mean'], label=condition,
            color=color, marker=marker, linestyle=linestyle, linewidth=2, markersize=4
        )
        
        # Plot the standard deviation fill
        ax.fill_between(
            subset['Spinal Level'], subset['lower'], subset['upper'],
            color=color, alpha=0.3
        )
    ax.set_title(title)
    ax.grid(True)

# Plot each metric
plot_with_tags(axes[0], wa_summary, "WA()")
plot_with_tags(axes[1], improvement_summary, "% Improvement")
plot_with_tags(axes[2], signal_loss_summary, "Predicted Signal Loss")

# Adjust ticks to ensure they're on the correct side
for ax in axes:
    ax.tick_params(axis='y', which='both', left=False, right=True)
    ax.yaxis.set_label_position("right")
    ax.yaxis.tick_right()

# Show the plot
plt.tight_layout()
plt.show()
