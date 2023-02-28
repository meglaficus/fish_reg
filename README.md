# fish_reg

Simple program that uses rigid registration with Elastix to stabilise video of zebrafish under fluorescent microscope.

## Setup
```
pip install fish_reg
```

## Usage
Warning! There might be many warnings popping up while the video file is read for whatever reason. Just ignore these.



However you use it now it will save the corrected video in the same directory as the original video but with the suffix "_fixed".

<br>

Basic usage
```
fish_reg_execute path/to/file/or/directory
```

Define coarsness of registration (-r) and width of smoothing window (-w)
```
fish_reg_execute path/to/file.tif -r 2 -w 5
```
Using only slice of video to test performance. The start (-s) and end (-e) tags are optional and determine boundries of video slice.
```
fish_reg_execute path/to/file.tif -sl -s 500 -e 700
```


## Limitations
- Annoying warnings when reading video file
- Tested on single system, might have problems with data from other sources
- Only uses rigid registration, as of yet no option for deformable registration
