#!/bin/bash
# Compute mask used for analysis and register it to a reference EPI image
# Takes two parameters: the path to the reference EPI image and the path to the T1w image

REF_FOLDER_PATH=$1
t1w_PATH=$2

TARGET_PATH=$(find $REF_FOLDER_PATH -name "*_mc_mean.nii.gz")
SEG_PATH=$(find $REF_FOLDER_PATH -name "*sc_seg.nii.gz")
t1w_folder_path=$(dirname $t1w_PATH)

# OUTPUTS
T1w_SEG_FOLDER_PATH=$t1w_folder_path/seg
if [ ! -d "$T1w_SEG_FOLDER_PATH" ]; then
    mkdir -p $T1w_SEG_FOLDER_PATH
fi

T1w_WARP_FOLDER_PATH=$t1w_folder_path/warp
if [ ! -d "$T1w_WARP_FOLDER_PATH" ]; then
    mkdir -p $T1w_WARP_FOLDER_PATH
fi

T1w_IMAGES_FOLDER_PATH=$t1w_folder_path/images
if [ ! -d "$T1w_IMAGES_FOLDER_PATH" ]; then
    mkdir -p $T1w_IMAGES_FOLDER_PATH
fi

t1w_SEG_PATH=$T1w_SEG_FOLDER_PATH/T1w_seg.nii.gz
t1w_REG_PATH=$T1w_IMAGES_FOLDER_PATH/T1w_reg.nii.gz
t1w_SEG_REG_PATH=$T1w_SEG_FOLDER_PATH/T1w_seg_reg.nii.gz
WARP_PATH=$T1w_WARP_FOLDER_PATH/warp_t1w_to_EPI_REF.nii.gz

# Get SEG_PATH folder path
MASK_PATH=$REF_FOLDER_PATH/seg/sc_mask.nii.gz

# Create mask centered around the spinal cord in EPI
sct_create_mask -i $TARGET_PATH -p centerline,$SEG_PATH -size 25mm -f cylinder -o $MASK_PATH

# Create spinal cord mask for T1w
sct_deepseg -task seg_sc_contrast_agnostic -i $t1w_PATH -o $t1w_SEG_PATH -qc $t1w_folder_path/qc

# Register T1w to EPI
sct_register_multimodal -i $t1w_PATH -iseg $t1w_SEG_PATH -d $TARGET_PATH -dseg $SEG_PATH -param step=1,type=seg,algo=centermass \
    -qc $t1w_folder_path/qc -owarp $WARP_PATH \
    -o $t1w_REG_PATH

# Apply transformation to T1w segmentation
sct_apply_transfo -i $t1w_SEG_PATH -d $TARGET_PATH -w $WARP_PATH -x linear -o $t1w_SEG_REG_PATH

# Create labels
LABELS_FOLDER_PATH=$t1w_folder_path/labels
if [ ! -d "$LABELS_FOLDER_PATH" ]; then
    mkdir -p $LABELS_FOLDER_PATH
fi

#Look if labels exist
LABELS_PATH=$LABELS_FOLDER_PATH/labels.nii.gz
LABELS_REG_PATH=$LABELS_FOLDER_PATH/labels_reg.nii.gz
LABELS_SEG_REG_PATH=$LABELS_FOLDER_PATH/labels_seg_reg.nii.gz
if [ ! -f $LABELS_PATH ]; then
    # Create labels
    sct_label_utils -i $t1w_REG_PATH -create-viewer 2:8 -qc $t1w_folder_path/qc -o $LABELS_PATH
fi

# Register labels
sct_apply_transfo -i $LABELS_PATH -d $TARGET_PATH -w $WARP_PATH -x label -o $LABELS_REG_PATH

# Compute segmentation based on registered labels
sct_label_utils -i  $t1w_SEG_REG_PATH -disc $LABELS_REG_PATH -o $LABELS_SEG_REG_PATH