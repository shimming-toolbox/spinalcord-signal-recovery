#!/bin/bash
# Compute tSNR in the spinal cord
# Takes two parameters: the path to the tSNR script and the output path

EPI_60vol_PATH=$1
OUTPUT_PATH=$2
TEMP_PATH=$OUTPUT_PATH/temp

# Create temp directory if it doesn't exist
if [ ! -d $TEMP_PATH ]; then
  mkdir -p $TEMP_PATH
fi

# Get file name
FNAME=$(basename $EPI_60vol_PATH)
FNAME_NO_EXT="${FNAME%.*}"
FNAME_NO_EXT="${FNAME_NO_EXT%.*}"

# Compute mean image
EPI_mean_PATH=$TEMP_PATH/EPI_60vol_mean.nii.gz
fslmaths "$EPI_60vol_PATH" -Tmean $EPI_mean_PATH

# Get mask of the spinal cord
MASK_PATH=$OUTPUT_PATH/sc_seg.nii.gz
sct_deepseg -task seg_sc_contrast_agnostic -i $EPI_mean_PATH -o $MASK_PATH -qc $OUTPUT_PATH/qc

# Apply motion correction
EPI_mc_folder_path=$TEMP_PATH/EPI_moco
sct_fmri_moco -i $EPI_60vol_PATH -g 1 -o $EPI_mc_folder_path -qc $OUTPUT_PATH/qc -qc-seg $MASK_PATH -x nn
EPI_mc_path=$EPI_mc_folder_path/${FNAME_NO_EXT}_moco.nii.gz
EPI_mc_mean_path=$EPI_mc_folder_path/${FNAME_NO_EXT}_moco_mean.nii.gz
mv $EPI_mc_mean_path $OUTPUT_PATH/EPI_mc_mean.nii.gz

# Detrend data
EPI_detrend_path=$TEMP_PATH/EPI_detrend.nii.gz
detrend_file=$TEMP_PATH/detrend_1st_order.con
Ntp=$(fslnvols $EPI_mc_path)
awk -v Ntp="$Ntp" 'BEGIN { for (i = 1; i <= Ntp; i++) printf "1 \t %3d\n", i; }' > $detrend_file
fsl_glm -i $EPI_mc_path -d $detrend_file -o $TEMP_PATH/betas.nii.gz --out_res=$EPI_detrend_path

# Compute STD
EPI_std_path=$TEMP_PATH/EPI_std.nii.gz
fslmaths "$EPI_detrend_path" -Tstd $EPI_std_path

# Compute tSNR
tSNR_PATH=$OUTPUT_PATH/tSNR.nii.gz
fslmaths $EPI_mc_mean_path -div $EPI_std_path $tSNR_PATH
