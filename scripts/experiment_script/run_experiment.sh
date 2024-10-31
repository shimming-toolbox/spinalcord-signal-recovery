#!/bin/bash
echo "
This script runs the entire experiment for a given subject. It is meant to be run from the command line after
the baseline field map and one baseline EPI has been acquired. Your dicom folder should be organized as follows:
dicoms
├── 01_baseline_GRE (mag)
│   ├── dicom1
│   ├── dicom2
│   └── ...
|── 02_baseline_GRE (phase)
|    ├── dicom1
|    ├── dicom2
|    └── ...
|-- 03_baseline_EPI (AP or PA)
|    ├── dicom1
|    ├── dicom2
|    └── ...


It takes three arguments:
1. The path to the dicoms directory
2. The name / tag of the subject

Don't forget to change the global variables to match your setup and activate shimming-toolbox's conda
environement before running the script.
"

SCRIPT_DIR=$(dirname "$(realpath "$0")")
COIL_PROFILES_DIR="$SCRIPT_DIR/../../data/coil_profiles"

COIL_PATH="${COIL_PROFILES_DIR}/coil_profiles_NP15.nii.gz"
COIL_CONFIG_PATH="${COIL_PROFILES_DIR}/NP15_config.json"


# Check if two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters"
    echo "Usage: ./run_experiment.sh <dicoms_path> <subject_name>"
    exit 1
fi

# Assign the arguments to variables
DICOMS_PATH=$1
SUBJECT_NAME=$2

OUTPUT_PATH="${DICOMS_PATH%/*}/niftis_opt/"
SORTED_DICOMS_PATH="${DICOMS_PATH%/*}/sorted_dicoms_opt/"
COIL_NAME=$(jq -r '.name' $COIL_CONFIG_PATH)
echo NAME: $COIL_NAME
# Sorting dicoms
echo "Sorting dicoms"
st_sort_dicoms -i $DICOMS_PATH -o $SORTED_DICOMS_PATH -r

# Dicoms to nifti
echo "Converting dicoms to nifti"
st_dicom_to_nifti -i $SORTED_DICOMS_PATH --subject $SUBJECT_NAME -o $OUTPUT_PATH

# Set file paths
MAGNITUDE_PATH=$(find "${OUTPUT_PATH}tmp_dcm2bids/sub-${SUBJECT_NAME}" -name "*e1.nii.gz")
PHASE1_PATH=$(find "${OUTPUT_PATH}tmp_dcm2bids/sub-${SUBJECT_NAME}" -name "*e1_ph.nii.gz")
PHASE2_PATH=$(find "${OUTPUT_PATH}tmp_dcm2bids/sub-${SUBJECT_NAME}" -name "*e2_ph.nii.gz")
EPI_PATH=$(find "${OUTPUT_PATH}sub-${SUBJECT_NAME}/func" -name "*.nii.gz")
MPRAGE_PATH="${OUTPUT_PATH}sub-${SUBJECT_NAME}/anat/sub-${SUBJECT_NAME}_T1w.nii.gz"

# Create mask from magnitude image
echo "Creating mask from magnitude image"
MASK_DIR="${OUTPUT_PATH}derivatives/masks"
if [ ! -d $MASK_DIR ]; then
    mkdir $MASK_DIR
fi

FNAME_MASK_SCT_FM="${MASK_DIR}/sct_mask_40.nii.gz"
FNAME_MASK_SCT_OPT="${MASK_DIR}/sct_mask_25.nii.gz"
FNAME_CENTERLINE="${MASK_DIR}/centerline.nii.gz"
sct_deepseg_sc -i "${MPRAGE_PATH}" -c t1 -o "${FNAME_CENTERLINE}" || exit
sct_create_mask -i "${MPRAGE_PATH}" -p centerline,"${FNAME_CENTERLINE}" -size 25 -o "${FNAME_MASK_SCT_OPT}" || exit
sct_create_mask -i "${MPRAGE_PATH}" -p centerline,"${FNAME_CENTERLINE}" -size 40 -o "${FNAME_MASK_SCT_FM}" || exit

# Show masks with magnitude
fsleyes $MPRAGE_PATH -cm greyscale $FNAME_MASK_SCT_OPT -cm red -a 50.0 &

# Ask the user if the mask is good
echo "Does the mask look good?"
echo "1. Yes"
echo "2. No, I'll input my own mask"
echo "3. No, exit program"
read -p "Enter your choice (1 or 2): " mask_approval

case $mask_approval in
    1)
        echo "Mask approved."
        ;;
    2)
        read -p "Enter the path for the new mask: " new_mask_path
        ;;
    3)
        echo "Exiting."
        exit 1
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Create fieldmap
echo "Creating fieldmap"
FIELDMAP_PATH="${OUTPUT_PATH}derivatives/fmap/fieldmap.nii.gz"
FIELDMAP_JSON_PATH="${OUTPUT_PATH}derivatives/fmap/fieldmap.json"
st_prepare_fieldmap $PHASE1_PATH $PHASE2_PATH \
 --mag $MAGNITUDE_PATH \
 --unwrapper prelude \
 --gaussian-filter true \
 --mask $FNAME_MASK_SCT_FM \
 --sigma 1 \
 -o $FIELDMAP_PATH \

fsleyes $MAGNITUDE_PATH $FIELDMAP_PATH -dr -100 100

# Prompt user to approve fieldmap
echo "Does the fieldmap look good?"
echo "1. Yes"
echo "2. No"
read -p "Enter your choice (1 or 2): " fieldmap_approval

case $fieldmap_approval in
    1)
        echo "Fieldmap approved."
        ;;
    2)
        read -p "Enter the path for the new fieldmap: " new_fieldmap_path
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

# Shim the fieldmap
echo "Shimming the fieldmap"

# Create output directory
OPTI_OUTPUT_DIR="${OUTPUT_PATH}derivatives/optimizations"
if [ ! -d $OUTPUT_DIR ]; then
    mkdir $OUTPUT_DIR
fi


cp "${FIELDMAP_JSON_PATH}" "${PATH_OUTPUT_STATIC_012_DELTA_PI}/fieldmap_calculated_shim.json"

for w in 0 0.0001 0.01 1
do
    OUTPUT_DIR="${OPTI_OUTPUT_DIR}/dynamic_shim_${w}GZ"
    st_b0shim dynamic \
        --coil $COIL_PATH $COIL_CONFIG_PATH \
        --fmap $FIELDMAP_PATH \
        --anat $EPI_PATH \
        --mask $FNAME_MASK_SCT_OPT \
        --mask-dilation-kernel-size 5 \
        --optimizer-criteria "grad" \
        --weighting-signal-loss $w \
        --optimizer-method "least_squares" \
        --slices "auto" \
        --output-file-format-coil "chronological-coil" \
        --output-value-format "absolute" \
        --fatsat "yes" \
        --regularization-factor 0.3 \
        --output $OUTPUT_DIR 

    DYN_CURRENTS_DIR="${OUTPUT_DIR}/coefs_coil0_${COIL_NAME}_no_fatsat.txt"
    DYN_CURRENTS_MODIFIED_DIR="${OUTPUT_DIR}/coefs_coil0_${COIL_NAME}_SAME_CURRENTS_FATSAT.txt"

    fatsat=$(sed -n '1p' $DYN_CURRENTS_DIR)

    sed 'p' $DYN_CURRENTS_DIR > $DYN_CURRENTS_MODIFIED_DIR

done

# Remove the sorted dicoms folder
rm -r $SORTED_DICOMS_PATH