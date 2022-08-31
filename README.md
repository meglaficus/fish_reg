# fish_reg

Simple program that uses rigid registration to stabilise video of zebrafish under electrophysiology microscope.

## Setup
```
pip install fish_reg
```

## Usage

Basic usage
```
fish_reg_execute path/to/file.tif
```
Perform on directory of files
```
fish_reg_execute path/to/directory -d
```
define coarsness of registration (-r) and width of smoothing window (-w)
```
fish_reg_execute path/to/file.tif -r 2 -w 5
```
Using only slice of video to test performance. The start (-s) and end (-e) tags are optional and determine boundries of video slice.
```
fish_reg_execute path/to/file.tif -sl -s 500 -e 700
```


## Limitations
- Tested on single system, might have problems with data from other sources
- Only works with .tif files
- Only uses rigid registration, as of yet no option for deformable registration
