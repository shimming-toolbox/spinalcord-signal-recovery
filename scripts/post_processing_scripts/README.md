Post-processing scripts for analysis

# How to run

1. Change your directory to `sc_singal_recovery/scripts/post_processing_scripts`
  ```
  cd <path to sc_singal_recovery/scripts/post_processing_scripts>
  ```
2. Run `tSNR_sc.sh` to compute tSNR maps for each shimming optimization
  ```
   ./tSNR_sc.sh <path to EPI-60_volumes> <OUTPUT_PATH>
  ```
3. Run `prepare_ref.sh` to compute and register the mask used for analysis. We use the dynamic shimming acquisition as a reference as it should be the least distorted EPI.
  ```
  ./prepare_ref.sh <REF_EPI_PATH> <t1w_PATH>
  ```
4. Run `register_tSNR.sh` to register every EPI and compute tSNR for every spinal cord level
  ```
  ./register_tSNR.sh <REF_FOLDER_PATH> <T1w_SEG_REG_PATH> <INPUT_FOLDER_PATH>
  ```
