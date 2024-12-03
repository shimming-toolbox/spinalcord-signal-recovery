import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# This script generates Figure 7 of the paper

# Get the directory of the script being run
script_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(script_dir, '../../data/mutli_w_subject_6_tSNR_data.csv')

# Load the data that was saved previously
df_all_subjects = pd.read_csv(data_path)

# Set up the figure and style
f, axes = plt.subplots(1,3, figsize=(15, 3.2))
sns.set(style="whitegrid")

# Use seaborn lineplot to plot the data with 95% confidence intervals
sns.lineplot(
    data=df_all_subjects,
    x='Spinal Level', y='WA()', hue='Condition',
    hue_order=['Baseline', 'DynShim', 'SigRec_w0001', 'SigRec', 'SigRec_w1'],
    markers=True, style='Condition', dashes=False, 
    palette=['blue', 'green', 'purple', 'red', 'orange'],
    legend=False,
    ax=axes[0]
)

# Customize subplot
axes[0].grid(True)

sns.lineplot(
    data=df_all_subjects,
    x='Spinal Level', y='% Improvement', hue='Condition',
    hue_order=['Baseline', 'DynShim', 'SigRec'],
    markers=True, style='Condition', dashes=False, 
    palette=['blue', 'green', 'red'],
    orient='x',
    legend=False,
    ax=axes[1]
)
axes[1].grid(True)

# Sig loss plot
sns.lineplot(
    data=df_all_subjects,
    x='Spinal Level', y='Predicted signal Loss', hue='Condition',
    hue_order=['Baseline', 'DynShim', 'SigRec_w0001', 'SigRec', 'SigRec_w1'],
    markers=True, style='Condition', dashes=False, 
    palette=['blue', 'green', 'purple', 'red', 'orange'],
    legend=False,
    ax=axes[2]
)
axes[2].grid(True)
# Show the plot
plt.show()