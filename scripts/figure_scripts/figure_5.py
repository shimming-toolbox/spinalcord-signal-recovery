import nibabel as nib
import matplotlib.pyplot as plt
from scipy.ndimage import center_of_mass
import os

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


# Load data
script_dir = os.path.dirname(os.path.abspath(__file__))
EPIS_AP_PATHS = [
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/Baseline_EPI_AP.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/DynShim_EPI_AP.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/SigRec_w0001_EPI_AP.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/SigRec_w01_EPI_AP.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/SigRec_w1_EPI_AP.nii.gz")
]

EPIS_PA_PATHS = [
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/Baseline_EPI_PA.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/DynShim_EPI_PA.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/SigRec_w0001_EPI_PA.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/SigRec_w01_EPI_PA.nii.gz"),
    os.path.join(script_dir, "../../data/subject_6/derivatives/EPIs/SigRec_w1_EPI_PA.nii.gz")
]


SEGMENTATION_NII = os.path.join(script_dir, "../../data/subject_6/post_processing_data/T1w/seg/T1w_seg_reg.nii.gz")

# Load images
EPIs_AP = [nib.load(EPI_AP_PATH).get_fdata() for EPI_AP_PATH in EPIS_AP_PATHS]
EPIs_PA = [nib.load(EPI_PA_PATH).get_fdata() for EPI_PA_PATH in EPIS_PA_PATHS]

segmentation = nib.load(SEGMENTATION_NII).get_fdata()

# Binarize segmentation to get the spinal cord mask
mask = segmentation.astype(bool)

# Plot EPI images and segmentation
slices = [5, 24]
vmin = 0
vmax = 200
for slice in slices:
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    center = center_of_mass(mask[:, :, slice])
    center = (int(center[0]), int(center[1]))
    for i, (epi_ap, epi_pa) in enumerate(zip(EPIs_AP, EPIs_PA)):
        epi_ap = crop_center(epi_ap[:, :, slice], center, 32)
        epi_pa = crop_center(epi_pa[:, :, slice], center, 32)
        contour_crop = crop_center(mask[:, :, slice], center, 32)
        
        ax_ap = axes[0, i]
        ax_ap.imshow(epi_ap.T, cmap='gray', origin='lower', vmin=vmin, vmax=vmax)
        ax_ap.contour(contour_crop.T, colors='red')
        ax_ap.axis('off')
        
        ax_pa = axes[1, i]
        ax_pa.imshow(epi_pa.T, cmap='gray', origin='lower', vmin=vmin, vmax=vmax)
        ax_pa.contour(contour_crop.T, colors='red')
        ax_pa.axis('off')

    plt.tight_layout()
    plt.show()