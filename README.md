# spinalcord-signal-recovery
Scripts for signal recovery analysis in the spinal cord</br>
*NOTE* -- The bash scripts can only be run on Unix-based operating systems.
### Before starting
Before using these scripts, you need to:
1. Install dependencies
* [Anaconda or Miniconda](https://www.anaconda.com/download/success)
* [Shimming Toolbox's v1.1](https://github.com/shimming-toolbox/shimming-toolbox/releases/tag/1.1)
```
git clone -b 1.1 https://github.com/shimming-toolbox/spinalcord-signal-recovery.git ~/shimming-toolbox/
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
git clone https://github.com/4rnaudB/spinalcord-signal-recovery.git
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
* Experiment scripts are scripts used at the scanner during the acquisition to obtain the shimming coefficients
* Post-processing scripts are the scripts used to process the data into tSNR measurements
* Figure scripts are the different scripts used to create the paper's figures.
