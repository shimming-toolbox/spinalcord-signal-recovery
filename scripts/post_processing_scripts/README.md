Post-processing scripts for analysis

*** Make sure you are in the repo before starting ***

# How to run
1. Download the data (from the release and add the folder to the repo (spinalcord-signal-recovery/data)
2. Change your directory to `sc_singal_recovery/scripts/post_processing_scripts`
  ```
  cd ./scripts/post_processing_scripts
  ```

### If you want to run everything at once
3.1 Run the main script for every subject
  ```
  ./run_all.sh ../../data/subject_1/post_processing_data
  ```

### If you want to run every script separately:
3.2 Run `tSNR_sc.sh` to compute tSNR maps for each shimming optimization
  ```
  ./tSNR_sc.sh ../../data/subject_1/post_processing_data/Baseline/EPIs/Baseline_EPI_60vol.nii.gz Baseline
  ./tSNR_sc.sh ../../data/subject_1/post_processing_data/DynShim/EPIs/DynShim_EPI_60vol.nii.gz DynShim
  ./tSNR_sc.sh ../../data/subject_1/post_processing_data/SigRec/EPIs/SigRec_EPI_60vol.nii.gz SigRec
  ```
4. Run `prepare_ref.sh` to compute and register the mask used for analysis. We use the dynamic shimming acquisition as a reference as it should be the least distorted EPI.
  ```
  ./prepare_ref.sh ../../data/subject_1/post_processing_data/DynShim ../../data/subject_1/post_processing_data/T1w/T1w.nii
  ```
5. Run `register_tSNR.sh` to register every EPI and compute tSNR for every spinal cord level
  ```
  ./register_tSNR.sh ../../data/subject_1/post_processing_data/DynShim ../../data/subject_1/post_processing_data/T1w ../../data/subject_1/post_processing_data/DynShim
  ./register_tSNR.sh ../../data/subject_1/post_processing_data/DynShim ../../data/subject_1/post_processing_data/T1w ../../data/subject_1/post_processing_data/Baseline
  ./register_tSNR.sh ../../data/subject_1/post_processing_data/DynShim ../../data/subject_1/post_processing_data/T1w ../../data/subject_1/post_processing_data/SigRec
  ```
