import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import center_of_mass
from nibabel.processing import resample_from_to
import os

# This script generates Figure 4 of the paper


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

# Load the data
script_dir = os.path.dirname(os.path.abspath(__file__))
EPI_PATHS = [os.path.join(script_dir, "../../data/subject_6/post_processing_data/Baseline/EPIs/Baseline_EPI_mc_mean.nii.gz"),
                os.path.join(script_dir, "../../data/subject_6/post_processing_data/DynShim/EPIs/DynShim_EPI_mc_mean.nii.gz"),
                os.path.join(script_dir, "../../data/subject_6/post_processing_data/SigRec/EPIs/SigRec_EPI_mc_mean.nii.gz")]

MASK_PATH = os.path.join(script_dir, "../../data/subject_6/experiment_data/sub-6/derivatives/masks/sct_mask_25.nii.gz")

EPIs = [nib.load(EPI_PATH) for EPI_PATH in EPI_PATHS]
mask = nib.load(MASK_PATH)
mask = resample_from_to(mask, EPIs[0], order=0)

# Get mask
mask_data = mask.get_fdata().astype(bool)

# Get the data
crop_size = 32
EPIs_data = [EPI.get_fdata() for EPI in EPIs]
data_crop = np.zeros((crop_size, crop_size, EPIs_data[0].shape[2]))
mosaics = []
# Crop the center of the data
for EPI_data in EPIs_data:
    for slice in range(EPI_data.shape[-1]):
        center = center_of_mass(mask_data[:, :, slice])
        center = (int(center[0]), int(center[1]))
        data_crop[:, :, slice] = crop_center(EPI_data[:, :, slice], center, crop_size)
        
    data = data_crop[:, :, ::-1]
    mosaics.append(np.concatenate([np.rot90(data[:, :, i]) for i in range(data.shape[2])], axis=1))

mosaic_repeated = np.concatenate(mosaics, axis=0)

# Plot the mosaic
plt.figure(figsize=(10, 6))
plt.imshow(mosaic_repeated, cmap='gray', vmin=0, vmax=200)
plt.axis('off')
plt.show()
