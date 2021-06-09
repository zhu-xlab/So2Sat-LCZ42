# So2Sat-LCZ42
Zhu et al., So2Sat LCZ42: A Benchmark Dataset for Global Local Climate Zones Classification, IEEE Geoscience and Remote Sensing Magazine, in press, 2020. 

## Authors: 
Xiaoxiang Zhu, Jingliang Hu, Chunping Qiu, Yilei Shi, Jian Kang, Lichao Mou, Hossein Bagheri, Matthias Haeberle, Yuansheng Hua, Rong Huang, Lloyd Hughes, Hao Li, Yao Sun, Guichen Zhang, Shiyao Han, Michael Schmitt, Yuanyuan Wang

## Institute
Signal Processing in Earth Observation, Technical University of Munich, and Remote Sensing Technology Institute, German Aerospace Center.

## Funding 
This work is funded by European Research Council starting Grant: 

So2Sat: Big Data for 4D Global Urban Mapping - 10^16 Bytes from Social Media to Earth Observation Satellites
# Project website: http://www.so2sat.eu/
# 
# Team website: http://www.sipeo.bgu.tum.de/
#
# ******************************************************************************************

# Description of the files
training.h5:	training data containing SEN1, SEN2 patches and label
	sen1:	N*32*32*8
	sen2:	N*32*32*10
	label:	N*17 (one-hot coding)
	
validation.h5:  validation data containing similar SEN1, SEN2, and label
	sen1:  	M*32*32*8 
	sen2:  	M*32*32*10
	label: 	M*17 (one-hot coding)
	
testing.h5:	testing data containing only SEN1 and SEN2 patches, 
	sen1:  	L*32*32*8
	sen2:  	L*32*32*10
	label:  L*17 (one-hot coding)

read_file.py:	a demo python script to read in the files, and visualize a pair of patches
		Required python packages: h5py, numpy, and matplotlib.

*note:		testing.h5 will be released in a future version of this dataset


# Description of the content of sen1
Sentinel-1 data bands (the 4th dimension of data):
	1st band: Real part of original VH complex signal
	2nd band: Imaginary part of original VH complex signal
	3rd band: Real part of original VV complex signal
	4th band: Imaginary part of original VV complex signal
	5th band: Intensity of lee filtered VH signal
	6th band: Intensity of lee filtered VV signal
	7th band: Real part of lee filtered PolSAR covariance matrix off-diagonal element
	8th band: Imaginary part of lee filtered PolSAR covariance matrix off-diagonal element

Pixel size: 10m by 10m


# Description of the content of sen2
Sentinel-2 data bands (the 4th dimension of data):
	1st band: B2
	2nd band: B3
	3rd band: B4
	4th band: B5
	5th band: B6
	6th band: B7
	7th band: B8
	8th band: B8A
	9th band: B11 SWIR 
	10th band: B12 SWIR 

Pixel size: 10m by 10m

Details about the bands can be found: https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/overview


You can download the data from
https://mediatum.ub.tum.de/1454690


The data can be accessed by TensorFlow API directly:
https://www.tensorflow.org/datasets/catalog/so2sat
