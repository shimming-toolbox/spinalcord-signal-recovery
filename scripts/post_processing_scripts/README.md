Post-processing scripts for analysis

*** Make sure you are in the repo before starting ***

# How to run
1. Download the data (from the release and add the folder to the repo (spinalcord-signal-recovery/data)
2. Change your directory to `sc_singal_recovery/scripts/post_processing_scripts`
  ```
  cd ./scripts/post_processing_scripts
  ```
2. Run `tSNR_sc.sh` to compute tSNR maps for each shimming optimization
  ```
  ./tSNR_sc.sh ../../data/acdc_241/Baseline/EPIs/Baseline_EPI_60vol.nii.gz Baseline
  ./tSNR_sc.sh ../../data/acdc_241/DynShim/EPIs/DynShim_EPI_60vol.nii.gz DynShim
  ./tSNR_sc.sh ../../data/acdc_241/SigRec/EPIs/SigRec_EPI_60vol.nii.gz SigRec
  ```
3. Run `prepare_ref.sh` to compute and register the mask used for analysis. We use the dynamic shimming acquisition as a reference as it should be the least distorted EPI.
  ```
  ./prepare_ref.sh ../../data/acdc_241/DynShim ../../data/acdc_241/T1w/MPRAGE_Unifized.nii
  ```
4. Run `register_tSNR.sh` to register every EPI and compute tSNR for every spinal cord level
  ```
  ./register_tSNR.sh ../../data/acdc_241/DynShim ../../data/acdc_241/T1w ../../data/acdc_241/DynShim
  ./register_tSNR.sh ../../data/acdc_241/DynShim ../../data/acdc_241/T1w ../../data/acdc_241/Baseline
  ./register_tSNR.sh ../../data/acdc_241/DynShim ../../data/acdc_241/T1w ../../data/acdc_241/SigRec
  ```
