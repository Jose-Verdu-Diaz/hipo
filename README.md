# Hyperion_jvd

Tool for processing and analysing hyperion imaging.

## Disclaimer

This is a work-in-progress tool. Many bugs may arise and features will be added with time.
If you discover a bug or have a feature suggestion, do not hesitate to open an Issue.

## Setup

Check conda is installed in PATH:
```console
$ conda -V
conda 3.7.0
```
Update conda:
```console
$ conda update conda
```

Create conda environment. This project has been created for Python 3.10.2 and won't be 
maintained for any other version.
```console
$ conda create -n envname python=3.10.2
```

Activate the environment
```console
$ conda activate envname
```

Install required libraries
```console
$ conda install pandas
$ conda install pillow
$ conda install tifffile
$ conda install matplotlib
$ conda install seaborn
$ conda install seaborn_image
$ conda install tqdm
```

Run the tool
```console
$ python main.py
```

## Add a new sample

Choones option `2 - Add new sample` from the main menu, you will be prompted to enter 
a name for the sample. After entering a name, you will be forced to add three files
inside `samples/<samplename>/input`:
 - The image tiff file
 - The summary txt file
 - The annotation geojson file
After including all the files, you will be able to proceed.

## Considerations

Try not to modify the files and directories generated under the 'samples' directory, as it
would casue some bugs. The tool itself provides options to interact with the data.