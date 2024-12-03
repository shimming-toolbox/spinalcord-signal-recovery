import numpy as np
import matplotlib.pyplot as plt
import nibabel as nib
from nibabel.processing import resample_from_to
from scipy.ndimage import center_of_mass
import os

# This script generates Figure 3 of the paper


def crop_center(data, center, size):
    """
    Crops a square region around the center of the data.

    Args:
        data (ndarray): 2D data to be cropped
        center (tuple): (row, col) coordinates of the center
        size (int): Size of the square region to crop
        
    Returns:
        ndarray: Cropped 2D data
    """
    row, col = center
    half_size = size // 2
    row_start = max(0, row - half_size)
    row_end = min(data.shape[0], row + half_size)
    col_start = max(0, col - half_size)
    col_end = min(data.shape[1], col + half_size)
    return data[row_start:row_end, col_start:col_end]

# Data path
# Get the directory of the script being run
script_dir = os.path.dirname(os.path.abspath(__file__))

EPI_PATHS = [
    os.path.join(script_dir, "../../data/subject_6/post_processing_data/Baseline/EPIs/Baseline_EPI_mc_mean.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/post_processing_data/DynShim/EPIs/DynShim_EPI_mc_mean.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/post_processing_data/SigRec_w0001/EPIs/SigRec_w0001_EPI_mc_mean.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/post_processing_data/SigRec/EPIs/SigRec_EPI_mc_mean.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/post_processing_data/SigRec_w1/EPIs/SigRec_w1_EPI_mc_mean.nii.gz")
]

SIGLOSSMAP_PATHS = [
    os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/optimizations/dynamic_shim_0.01GZ/signal_loss_unshimmed.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/optimizations/dynamic_shim_0GZ/signal_loss_shimmed.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/optimizations/dynamic_shim_0.0001GZ/signal_loss_shimmed.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/optimizations/dynamic_shim_0.01GZ/signal_loss_shimmed.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/optimizations/dynamic_shim_1GZ/signal_loss_shimmed.nii.gz")
]

FM_PATHS = [
    os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/Baseline_fm.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/DynShim_fm.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/SigRec_w0001_fm.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/SigRec_fm.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/field_maps/SigRec_w1_fm.nii.gz")
]

MASK_PATH = os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/masks/sct_mask_25.nii.gz")
T1w_PATH = os.path.join(script_dir, "../../data/subject_6/post_processing_data/T1w/T1w.nii")

# Load data
epi_data = [nib.load(path).get_fdata() for path in EPI_PATHS]
siglossmap_nii = [nib.load(path) for path in SIGLOSSMAP_PATHS]
fm_data = [nib.load(path).get_fdata() for path in FM_PATHS]

baseline_nii = nib.load(EPI_PATHS[0])

siglossmap_resampled = [resample_from_to(nii, baseline_nii) for nii in siglossmap_nii]
siglossmap_data = [resampled.get_fdata() for resampled in siglossmap_resampled]

fm_resampled = [resample_from_to(nib.load(path), baseline_nii) for path in FM_PATHS]
fm_data = [resampled.get_fdata() for resampled in fm_resampled]

mask_nii = nib.load(MASK_PATH)
mask_resampled = resample_from_to(mask_nii, baseline_nii, order=0)
mask = mask_resampled.get_fdata().astype(bool)

# Calculate mean signal loss for slice 3
slice = 3
mean_sigloss = [np.nanmean(siglossmap[:, :, slice][mask[..., slice]]) for siglossmap in siglossmap_data]

# Crop the data around the center of mass
crop_size = 32  # Define the size of the square region to crop
center = center_of_mass(mask[:, :, slice])
center = (int(center[0]), int(center[1]))

# Crop the data around the center
epi_crop = [crop_center(epi[:, :, slice], center, crop_size) for epi in epi_data]
siglossmap_crop = [crop_center(siglossmap[:, :, slice]*mask[..., slice], center, crop_size) for siglossmap in siglossmap_data]
fm_crop = [crop_center(fm[:, :, slice], center, crop_size) for fm in fm_data]
contour_crop = crop_center(mask[:, :, slice], center, crop_size)

# Plot figure
vmin = 0
vmax = 128
fig, axes = plt.subplots(3, 5, figsize=(8, 6), gridspec_kw={'wspace': 0.005})

for i in range(5):
    axes[0, i].imshow(np.rot90(fm_crop[i]), cmap="bwr", vmin=-100, vmax=100)
    axes[1, i].imshow(np.rot90(siglossmap_crop[i]), cmap="hot", vmin=0, vmax=1)
    axes[2, i].imshow(np.rot90(epi_crop[i]), cmap="gray", vmin=vmin, vmax=vmax)
    axes[0, i].axis("off")
    axes[1, i].axis("off")
    axes[2, i].axis("off")
    
    # Add contour mask
    axes[0, i].contour(np.rot90(contour_crop), colors="cyan")
    axes[1, i].contour(np.rot90(contour_crop), colors="cyan")
    axes[2, i].contour(np.rot90(contour_crop), colors="cyan")
    
    # Add B0 RMSE field map annotations
    axes[0, i].text(0.5, 1, f'RMSE: {np.sqrt(np.nanmean(fm_crop[i]**2)):.2f}', ha='center', va='bottom', transform=axes[0, i].transAxes)
    # Add mean signal loss annotations
    axes[1, i].text(0.5, -0.2, f'Mean: {mean_sigloss[i]:.2f}', ha='center', va='top', transform=axes[0, i].transAxes)

fig.tight_layout(pad=0.05)
# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
fig.colorbar(plt.cm.ScalarMappable(cmap="hot", norm=plt.Normalize(vmin=0, vmax=1)), cax=cbar_ax, label="Signal loss")
plt.show()
