# So2Sat-LCZ42
## A visualization of selected samples
![so2sat_lcz42_sample_visualization](https://github.com/zhu-xlab/So2Sat-LCZ42/blob/master/so2sat_lcz42.JPG)
>This figure is cited from the following paper
## Paper
Xiao Xiang Zhu, Jingliang Hu, Chunping Qiu, Yilei Shi, Jian Kang, Lichao Mou, Hossein Bagheri, Matthias Haberle, Yuansheng Hua, Rong Huang, Lloyd Hughes, Hao Li, Yao Sun, Guichen Zhang, Shiyao Han, Michael Schmitt, Yuanyuan Wang (2020). So2Sat LCZ42: A Benchmark Data Set for the Classification of Global Local Climate Zones [Software and Data Sets]. IEEE Geoscience and Remote Sensing Magazine, 8(3), pp. 76–89. [Paper](https://ieeexplore.ieee.org/document/9014553)

```bibtex
@ARTICLE{Zhu2020So2Sat,
  author={Zhu, Xiao Xiang and Hu, Jingliang and Qiu, Chunping and Shi, Yilei and Kang, Jian and Mou, Lichao and Bagheri, Hossein and Haberle, Matthias and Hua, Yuansheng and Huang, Rong and Hughes, Lloyd and Li, Hao and Sun, Yao and Zhang, Guichen and Han, Shiyao and Schmitt, Michael and Wang, Yuanyuan},
  journal={IEEE Geoscience and Remote Sensing Magazine}, 
  title={So2Sat LCZ42: A Benchmark Data Set for the Classification of Global Local Climate Zones [Software and Data Sets]}, 
  year={2020},
  volume={8},
  number={3},
  pages={76-89},
  doi={10.1109/MGRS.2020.2964708}}
```

## Data Download
### Technical University of Munich:
[First version](https://mediatum.ub.tum.de/1459256?show_id=1454690): 

	This version is designed for an Alibaba AI Challenge (https://tianchi.aliyun.com/competition/entrance/231683/introduction)
	Training: 	42 cities around the world
	Validation:	western half of 10 other cities covering 10 cultural zones	

[Second version](https://mediatum.ub.tum.de/1459256?show_id=1483140):

	This version completes the first version with the testing data
	Training: 	42 cities around the world
	Validation:	western half of 10 other cities covering 10 cultural zones
	Testing:	eastern half of the 10 other cities	

[Third version](https://mediatum.ub.tum.de/1613658):

	This is the "3 splits version" of the So2Sat LCZ42 dataset. It provides three training/testing data split scenarios:
	1. Random split: every city 80% training / 20% testing (randomly sampled)
	2. Block split: every city is split in a geospatial 80%/20%-manner
	3. Cultural 10: 10 cities from different cultural zones are held back for testing purposes
### TensorFlow API:
https://www.tensorflow.org/datasets/catalog/so2sat


## Institute
[Signal Processing in Earth Observation](http://www.sipeo.bgu.tum.de/), Technical University of Munich, and Remote Sensing Technology Institute, German Aerospace Center.

## Funding 
This work is funded by European Research Council starting Grant: 

[So2Sat](http://www.so2sat.eu/): Big Data for 4D Global Urban Mapping - 10^16 Bytes from Social Media to Earth Observation Satellites

## Description of the files
training.h5:	training data containing SEN1, SEN2 patches and label

	sen1:	N*32*32*8	
	sen2:	N*32*32*10
	label:	N*17 (one-hot coding)
	
validation.h5:  validation data containing similar SEN1, SEN2, and label

	sen1:  	M*32*32*8 	
	sen2:  	M*32*32*10	
	label: 	M*17 (one-hot coding)
	
testing.h5:	testing data containing SEN1, SEN2 patches and label

	sen1:  	L*32*32*8
	sen2:  	L*32*32*10
	label:  L*17 (one-hot coding)

read_file.py:	a demo python script to read in the files, and visualize a pair of patches
		Required python packages: h5py, numpy, and matplotlib.


## Description of the content of sen1
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


## Description of the content of sen2
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

The pixel values are devided by 10,000 to decimal reflectance.

Details about the bands can be found: https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/overview


## Adding geolocation (2025 update!)
We release the geolocation information for each patch in the dataset, extending the [second version](https://mediatum.ub.tum.de/1459256?show_id=1483140) (culture-10) to the [fourth version](https://mediatum.ub.tum.de/1836598). You can also download this version from [HuggingFace](https://huggingface.co/datasets/zhu-xlab/So2Sat-LCZ42).

```
# These are the same as the second version. If you have already downloaded them, you don't need to download them again.
- training.h5
	- sen1:	N*32*32*8	
	- sen2:	N*32*32*10
	- label: N*17 (one-hot coding)
- validation.h5
- testing.h5

# These are geolocation data in the same order as the image data.
- training_geo.h5
	- coord: N*6 # UTM X, UTM Y, SEN1 row number, SEN1 col number, SEN2 row number, SEN2 col number
	- epsg: N*1 # EPSG code
	- tfw: N*6 # six parameters used to generate a TFW file
- validation_geo.h5
- testing_geo.h5

```

We provide a demo notebook [`demo_geotiff.ipynb`](demo_geotiff.ipynb) to load the image and geolocation, and generate a geotiff file from them.

