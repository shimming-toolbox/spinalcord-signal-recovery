#!/bin/bash
# Compute tSNR in the spinal cord
# Takes two parameters: the path to the tSNR script and the optimization name

EPI_60vol_PATH=$1
OPT_NAME=$2
EPI_FOLDER_PATH=$(dirname $EPI_60vol_PATH)
OPT_FOLDER_PATH=$(dirname $EPI_FOLDER_PATH)
TEMP_PATH=$OPT_FOLDER_PATH/temp
SEG_FOLDER_PATH=$OPT_FOLDER_PATH/seg
QC_FOLDER_PATH=$OPT_FOLDER_PATH/qc
tSNR_OUTPUT_PATH=$OPT_FOLDER_PATH/tSNR

# Create temp directory if it doesn't exist
if [ ! -d $TEMP_PATH ]; then
  mkdir -p $TEMP_PATH
fi

# Create Seg directory if it doesn't exist
if [ ! -d $SEG_FOLDER_PATH ]; then
  mkdir -p $SEG_FOLDER_PATH
fi

# Create tSNR directory if it doesn't exist
if [ ! -d $tSNR_OUTPUT_PATH ]; then
  mkdir -p $tSNR_OUTPUT_PATH
fi

# Get file name
FNAME=$(basename $EPI_60vol_PATH)
FNAME_NO_EXT="${FNAME%.*}"
FNAME_NO_EXT="${FNAME_NO_EXT%.*}"

# Compute mean image
EPI_mean_PATH="${EPI_FOLDER_PATH}/${OPT_NAME}_EPI_60vol_mean.nii.gz"
fslmaths $EPI_60vol_PATH -Tmean $EPI_mean_PATH

# Get mask of the spinal cord
MASK_PATH=$SEG_FOLDER_PATH/sc_seg.nii.gz
sct_deepseg -task seg_sc_contrast_agnostic -i $EPI_mean_PATH -o $MASK_PATH -qc $QC_FOLDER_PATH

# Create mask centered around the spinal cord in EPI
MOCO_MASK_PATH=$SEG_FOLDER_PATH/sc_mask.nii.gz
sct_create_mask -i $EPI_mean_PATH -p centerline,$MASK_PATH -size 25mm -f cylinder -o $MOCO_MASK_PATH

# Apply motion correction
EPI_mc_folder_path=$EPI_FOLDER_PATH/MOCO
sct_fmri_moco -i $EPI_60vol_PATH -g 1 -o $EPI_mc_folder_path -qc $QC_FOLDER_PATH -qc-seg $MOCO_MASK_PATH -m $MOCO_MASK_PATH \
    -param poly=0,smooth=0,gradStep=1,sampling=None,numTarget=0,iterAvg=1

EPI_mc_path=$EPI_mc_folder_path/${FNAME_NO_EXT}_moco.nii.gz
EPI_mc_mean_path=$EPI_mc_folder_path/${FNAME_NO_EXT}_moco_mean.nii.gz

mv $EPI_mc_mean_path $EPI_FOLDER_PATH/${OPT_NAME}_EPI_mc_mean.nii.gz
EPI_mc_mean_path=$EPI_FOLDER_PATH/${OPT_NAME}_EPI_mc_mean.nii.gz

mv $EPI_mc_path $EPI_FOLDER_PATH/${OPT_NAME}_EPI_60vol_mc.nii.gz
EPI_mc_path=$EPI_FOLDER_PATH/${OPT_NAME}_EPI_60vol_mc.nii.gz

# Detrend data
EPI_detrend_path=$TEMP_PATH/${OPT_NAME}_EPI_detrend.nii.gz
detrend_file=$TEMP_PATH/detrend_1st_order.con
Ntp=$(fslnvols $EPI_mc_path)
awk -v Ntp="$Ntp" 'BEGIN { for (i = 1; i <= Ntp; i++) printf "1 \t %3d\n", i; }' > $detrend_file
fsl_glm -i $EPI_mc_path -d $detrend_file -o $TEMP_PATH/betas.nii.gz --out_res=$EPI_detrend_path

# Compute STD
EPI_std_path=$TEMP_PATH/EPI_std.nii.gz
fslmaths "$EPI_detrend_path" -Tstd $EPI_std_path

# Compute tSNR
tSNR_PATH=$tSNR_OUTPUT_PATH/${OPT_NAME}_tSNR.nii.gz
fslmaths $EPI_mc_mean_path -div $EPI_std_path $tSNR_PATH
