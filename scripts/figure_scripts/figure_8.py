import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import nibabel as nib
from nibabel.processing import resample_from_to as nib_resample_from_to
import pandas as pd
from scipy.stats import mannwhitneyu
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
            ['Baseline'] * len(rmses[0]) + ['DynShim'] * len(rmses[1]) + ['SigRec'] * len(rmses[2])
        )
        all_data['Slice'].extend(list(range(len(rmses[0]))) * len(rmses))  # Slice index
        all_data['Subject'].extend([subject_data['name']] * (len(rmses[0]) * len(rmses)))
    
    # Create a DataFrame from the collected data
    df = pd.DataFrame(all_data)
    
    return df

def violin_plot_rmses_subjects(df):
    # Create the violin plot with hue based on the subject
    plt.figure(figsize=(15, 6))
    sns.violinplot(x='Shim', y='RMSE', hue='Subject', data=df, cut=0, scale='width', legend=True)
    # Formatting
    plt.xticks(ticks=[0, 1, 2], labels=['Baseline', 'DynShim', 'SigRec'])
    plt.ylabel('RMSE')
    plt.title('Slice-wise RMSE Distribution Across Subjects')
    plt.legend(title='Subject', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.ylim(-15, 150)
    # plt.gca().margins(x=0.1)  # Add extra space between groups
    plt.grid(axis='y')
    #remove legend
    plt.legend().remove()
    plt.show()

def make_combined_subject(subject_data_list):
    # combine all subjects into one
    combined_subject = {
        'name': 'All Subjects',
        'mask': np.nanmean(np.stack([subject_data['mask'] for subject_data in subject_data_list]), axis=0),
        'fms': [np.nanmean(np.stack([subject_data['fms'][i] for subject_data in subject_data_list]), axis=0) for i in range(3)]
    }
    compute_rmse_subject(combined_subject)
    return combined_subject
    
subject_data_list = []
script_dir = os.path.dirname(os.path.abspath(__file__))
for i, sub in enumerate(['1', '2', '3', '4', '5', '6']):
    subject_paths = {
        "mask_path": os.path.join(script_dir, f"../../data/subject_{sub}/experiment_data/sub-{sub}/derivatives/masks/sct_mask_25.nii.gz"),
        "fm_paths": [
                os.path.join(script_dir, f"../../data/subject_{sub}/derivatives/field_maps/Baseline_fm.nii.gz"),
                os.path.join(script_dir, f"../../data/subject_{sub}/derivatives/field_maps/DynShim_fm.nii.gz"),
                os.path.join(script_dir, f"../../data/subject_{sub}/derivatives/field_maps/SigRec_fm.nii.gz")
            ]
    }
    subject_data = load_subject_data(subject_paths, f'{i+1}')
    compute_rmse_subject(subject_data)
    subject_data_list.append(subject_data)

mean_subject = make_combined_subject(subject_data_list)
subject_data_list.append(mean_subject)

# create a DataFrame from the subject data
df = make_df_from_subject_data(subject_data_list)

# Plot violin plot with hue based on subject
violin_plot_rmses_subjects(df)

###
print("################## STATS ##################")
# Print mean and std from the combined subject
print(f"Mean RMSE: {mean_subject['rmses_mean']}")
print(f"Std RMSE: {mean_subject['rmses_std']}")

# PRint the p-values for the mean RMSEs of the combined subject
baseline = mean_subject['rmses'][0]
dynshim = mean_subject['rmses'][1]
sigrec = mean_subject['rmses'][2]
print(f"Baseline vs DynShim: {mannwhitneyu(baseline, dynshim)}")
print(f"Baseline vs SigRec: {mannwhitneyu(baseline, sigrec)}")
print(f"DynShim vs SigRec: {mannwhitneyu(dynshim, sigrec)}")
print(f"Baseline vs Baseline: {mannwhitneyu(baseline, baseline)}")