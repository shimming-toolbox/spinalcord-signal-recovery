#!/bin/bash

# Inputs
REF_FOLDER_PATH=$1
t1w_REF_SEG_REG_PATH=$2
INPUT_FOLDER_PATH=$3

REF_EPI_PATH="$REF_FOLDER_PATH/EPI_mc_mean.nii.gz"
REF_SEG_PATH="$REF_FOLDER_PATH/sc_seg.nii.gz"
REF_MASK_PATH="$REF_FOLDER_PATH/sc_mask.nii.gz"
INPUT_EPI_PATH="$INPUT_FOLDER_PATH/EPI_mc_mean.nii.gz"
EPI_REG_TO_REF=$INPUT_FOLDER_PATH/EPI_reg_to_ref.nii.gz
tSNR_PATH="$INPUT_FOLDER_PATH/tSNR.nii.gz"
INPUT_SEG_PATH="$INPUT_FOLDER_PATH/sc_seg.nii.gz"
LABELS_PATH=$(dirname $t1w_REF_SEG_REG_PATH)/labels_seg_reg.nii.gz

# OUTPUTS
WARP_PATH=$INPUT_FOLDER_PATH/warp_EPI_to_REF.nii.gz
tSNR_REG_PATH=$INPUT_FOLDER_PATH/tSNR_reg.nii.gz
MEAN_tSNR_PATH=$INPUT_FOLDER_PATH/mean_tSNR.csv
tSNR_PER_LEVEL_PATH=$INPUT_FOLDER_PATH/tSNR_perlevel.csv

# Register EPI to reference
sct_register_multimodal -i $INPUT_EPI_PATH -iseg $INPUT_SEG_PATH -d $REF_EPI_PATH -dseg $REF_SEG_PATH -m $REF_MASK_PATH \
    -param step=1,type=im,algo=slicereg,metric=CC,iter=20,poly=5,smooth=1 -qc $INPUT_FOLDER_PATH/qc \
    -o $EPI_REG_TO_REF -owarp $WARP_PATH

# Apply transformation to tSNR
sct_apply_transfo -i $tSNR_PATH -d $REF_EPI_PATH -w $WARP_PATH -x linear -o $tSNR_REG_PATH

# Compute mean tSNR
sct_extract_metric -i $tSNR_REG_PATH -f $t1w_REF_SEG_REG_PATH -method wa -perslice 0 -o $MEAN_tSNR_PATH

# Compute tSNR per level
sct_extract_metric -i $tSNR_REG_PATH -f $t1w_REF_SEG_REG_PATH -method wa -vertfile $LABELS_PATH -perlevel 1 -vert 2:8 -o $tSNR_PER_LEVEL_PATH