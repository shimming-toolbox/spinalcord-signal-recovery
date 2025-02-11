# spinalcord-signal-recovery

This repository includes a collection of scripts that were used to analyze the MRI data and generate figures for the article "Breheret et al. Impact of through-slice gradient optimization for dynamic slice-wise shimming in the cervico-thoracic spinal cord (in revision)".

> [!NOTE]  
> The bash scripts can only be run on Unix-based operating systems.

Citation:
```Coming soon```

### Before starting

Before using these scripts, you need to:
1. Install dependencies
* [Anaconda or Miniconda](https://www.anaconda.com/download/success)
* [Shimming Toolbox's v1.2](https://github.com/shimming-toolbox/shimming-toolbox/releases/tag/v1.2)
```
git clone -b v1.2 https://github.com/shimming-toolbox/shimming-toolbox/ ~/shimming-toolbox/
cd ~/shimming-toolbox/
make install
```
* [SCT v6.3](https://github.com/spinalcordtoolbox/spinalcordtoolbox/releases/tag/6.3)
```
git clone -b 6.3 https://github.com/spinalcordtoolbox/spinalcordtoolbox/ ~/spinalcordtoolbox/
cd ~/spinalcordtoolbox/
./install_sct
```
* [FSL](https://fsl.fmrib.ox.ac.uk/fsl/docs/#/install/index) (follow instructions on their website)
2. Clone the GitHub repository
```
cd <path_to_where_you_want_the_repository>
git clone https://github.com/shimming-toolbox/spinalcord-signal-recovery.git
```
3. Move to the repository
```
cd spinalcord-signal-recovery
```
4. Create a conda environment using the env.yml file
```
conda env create -n <name_of_your_env> -f env.yml
```
5. Activate the new environment
```
conda activate <name_of_your_env>
```
3. Download the data available on [OSF](https://osf.io/rs6tv/)
4. Place the unzipped data folder in this folder (spinalcord-signal-recovery)
* Note that the outputs are already provided in this folder.


### How to use

Navigate to the different script folders for specific instructions on how to run the different scripts. 
* [experiment_script](https://github.com/shimming-toolbox/spinalcord-signal-recovery/tree/main/scripts/experiment_script): These scripts are used at the scanner during the acquisition to obtain the shimming coefficients
* [post_processing_scripts](https://github.com/shimming-toolbox/spinalcord-signal-recovery/tree/main/scripts/post_processing_scripts): Process the data to generatetSNR measurements
* [figure_scripts](https://github.com/shimming-toolbox/spinalcord-signal-recovery/tree/main/scripts/figure_scripts): Generate figures for the paper
