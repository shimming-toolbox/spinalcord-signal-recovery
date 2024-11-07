import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nibabel as nib
from nibabel.processing import resample_from_to as nib_resample_from_to
import pandas as pd
import os

def load_subject_data(subject_paths, name):
    mask_img = nib.load(subject_paths["mask_path"])
    fm_imgs = [nib.load(fm_path) for fm_path in subject_paths["fm_paths"]]
    
    # resample mask to fm resolution
    mask_img = nib_resample_from_to(mask_img, fm_imgs[0], order=0)
    
    # Replace 0 with NaN in mask
    mask_img_data = mask_img.get_fdata()
    mask_img_data[mask_img_data == 0] = np.nan
    
    # apply mask to fm images
    fm_imgs_data = [fm_img.get_fdata() * mask_img_data for fm_img in fm_imgs]
    
    return {'name': name, 'mask':mask_img_data, 'fms': fm_imgs_data}

def compute_slice_wise_rsme(fm_data):
    rmses = []
    for slice_idx in range(fm_data.shape[-1]):
        fm_slice = fm_data[..., slice_idx]
        rmses.append(np.sqrt(np.nanmean(fm_slice ** 2)))
    return rmses

def compute_rmse_subject(subject_data):
    # create [] to store rmses if not already present
    if 'rmses' not in subject_data:
        subject_data['rmses'] = []
    for fm_img in subject_data['fms']:
        rmses = compute_slice_wise_rsme(fm_img)
        subject_data['rmses'].append(rmses)
    subject_data['rmses_mean'] = [np.nanmean(rmses) for rmses in subject_data['rmses']]
    subject_data['rmses_std'] = [np.nanstd(rmses) for rmses in subject_data['rmses']]
    
def make_df_from_subject_data(subject_data_list):
    all_data = {
        'RMSE': [],
        'Shim': [],
        'Slice': [],
        'Subject': []
    }
    
    # Loop over each subject's data and collect the RMSEs
    for subject_data in subject_data_list:
        rmses = subject_data['rmses']
        
        # Flatten the RMSE data and append to the all_data dict
        all_data['RMSE'].extend([rmse for rmse_list in rmses for rmse in rmse_list])
        all_data['Shim'].extend(
            ['Baseline'] * len(rmses[0]) + ['w = 0'] * len(rmses[1]) + ['w = 0.01'] * len(rmses[2]) + \
            ['w = 0.0001'] * len(rmses[3]) + ['w = 1'] * len(rmses[4])
        )
        all_data['Slice'].extend(list(range(len(rmses[0]))) * len(rmses))  # Slice index
        all_data['Subject'].extend([subject_data['name']] * (len(rmses[0]) * len(rmses)))
    
    # Create a DataFrame from the collected data
    df = pd.DataFrame(all_data)
    
    return df

def violin_plot_rmses_subjects(df):
    # Create the violin plot with hue based on the subject
    plt.figure(figsize=(15, 6))
    sns.violinplot(x='Shim', y='RMSE', hue='Shim', data=df, cut=0, legend=True)
    # Formatting
    plt.xticks(ticks=[0, 1, 2, 3, 4], labels=['Baseline', 'w = 0', 'w = 0.0001', 'w = 0.01', 'w = 1'])
    plt.ylabel('RMSE')
    plt.title('Slice-wise RMSE Distribution Across Subjects')
    plt.legend(title='Subject', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.ylim(-15, 150)
    plt.gca().margins(x=0.1)  # Add extra space between groups
    # Add horizontal gridlines
    plt.grid(axis='y')
    plt.show()   

script_dir = os.path.dirname(os.path.abspath(__file__))
subject_paths = {
    "mask_path": os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/masks/sct_mask_25.nii.gz"),
    "fm_paths": [
            os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/Baseline_fm.nii.gz"),
            os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/DynShim_fm.nii.gz"),
            os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/SigRec_w0001_fm.nii.gz"),
            os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/SigRec_fm.nii.gz"),
            os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/SigRec_w1_fm.nii.gz")
        ]
}

subject_data = load_subject_data(subject_paths, 'sub-6')
compute_rmse_subject(subject_data)

# Print mean and std from the combined subject
print(f"Mean RMSE: {subject_data['rmses_mean']}")
print(f"Std RMSE: {subject_data['rmses_std']}")

# create a DataFrame from the subject data
df = make_df_from_subject_data([subject_data])

# Plot violin plot with hue based on subject
violin_plot_rmses_subjects(df)