# ROOT to HDF5 Conversion

This Python code converts the ROOT output of Allpix-Squared into an HDF5 file for use with the NEUROPix project. Values retained are specific to those useful for NEUROPix analysis. 


This is the second step in the expected analysis pipeline.

## System requirements
- Python
- ROOT (typically sourced from central install)
- Allpix-Squared (typically sourced from central install)


## Getting started - setup
1. Clone code locally
`git clone https://github.com/neuropix-project/dataPipeline.git`
2. Ensure ROOT is activated, likely by sourcing the activation script `thisroot.sh`. This must be done for each new environment.
3. Confirm the presence of all required Python packages

`pip install -r requirements.txt`
4. Generate or copy ROOT files that were created with Allpix-Squared

## Running the code
1. Identify the location of the ROOT file you wish to convert and the Allpix-Squared library file `libAllpixObjects.so` (likely in `...allpix-squared/lib/`)
2. Run the code like:

`python root_to_hdf5.py -d <path to library file > -f <path to ROOT file>` 
By default, an HDF5 file with the same name as the original ROOT file will be created in the directory where the executable is saved. This can be changed with the commandline argument `-o`. Run `python root_to_hdf5.py -h` to see all input options.
