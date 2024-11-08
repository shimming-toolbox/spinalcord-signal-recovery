*** Make sure you are in the repo before starting ***
### How to run
1. Change the directory to this folder
```
cd ./scripts/experiment_scripts/
```
2. For subjects 1 to 5 only 2 w parameters were simulated
```
./run_experiment.sh ../../data/subject_1/experiment_data/dicoms_opt 1
```
3. For subject 6, 4 w parameters were simulated
```
./run_experiment_multi_w.sh ../../data/subject_6/experiment_data/dicoms_opt 6
```

### Extras
The field maps and EPIs in `data/derivatives/` were computed from the data available in dicom format in `data/experiment_data/dicoms_all`. To generate by yourself you can follow these instructions:
1. Sort dicoms
```
st_sort_dicoms -i ../../data/experiment_data/dicoms_all -o ../../sorted_dicoms
```
2. Convert dicoms to niftis
```
st_dicom_to_nifti -i ../../sorted_dicoms -o ../../nifits_all
```
3. Generate field maps
```
st_prepare_fieldmap <path_to_echo1_phase> <path_to_echo2_phase> \
 --mag <path_to_echo1_mag> \
 --unwrapper prelude \
 --mask <path_to_sct_mask_40> \
 --gaussian-filter true \
 --sigma 1 \
 -o <output_folder>
```
4. Generate EPIs
```
fslmaths <path_to_EPI> -Tmean <output_EPI>
```
