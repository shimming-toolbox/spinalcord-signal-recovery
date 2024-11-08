# spinalcord-signal-recovery
Scripts for signal recovery analysis in the spinal cord used in this paper: <insert links>

### Before starting
Before using these scripts, you need to:
1. Create a conda environment using the env.yml file
```
conda env create -n <name_of_your_env> -f env.yml
```
2. Activate the new environment
```
conda activate <name_of_your_env>
```
3. Download the data available > TO BE DECIDED
4. Place the unzipped data folder in this folder (spinalcord-signal-recovery) <br>
5. Download Shimming Toolbox's v1.1 <link>
6. Download [SCT v6.3](https://github.com/spinalcordtoolbox/spinalcordtoolbox/releases/tag/6.3)


### How to use
Navigate to the different script folders for specific instructions on how to run the different scripts. 
* Experiment scripts are scripts used at the scanner during the acquisition to obtain the shimming coefficients
* Post-processing scripts are the scripts used to process the data into tSNR measurements
* Figure scripts are the different scripts used to create the paper's figures.
