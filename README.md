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

Create conda environment. This project has been created for Python 3.10.2 and won't be maintained for any other version.
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