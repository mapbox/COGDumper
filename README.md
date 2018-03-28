# COG Dumper

[![Build Status](https://travis-ci.org/mapbox/COGDumper.svg?branch=master)](https://travis-ci.org/mapbox/COGDumper) [![codecov.io](https://codecov.io/github/mapbox/COGDumper/coverage.svg?token=Yd3y5aTvGo&branch=master)](https://codecov.io/github/mapbox/COGDumper?branch=master)

A python3 utility to extract a tile from a Cloud Optimized GeoTIFF (COG) without decompressing the contained data. Tiff data can be hosted locally, on a web server or S3.

This can be useful for serving compressed tiles from a TIFF without invoking Rasterio and GDAL. This utility has been tested with Tiff that have JPEG compression.

Tiled Tiff is an extension to TIFF 6.0 and more detail can be found [here](http://www.alternatiff.com/resources/TIFFphotoshop.pdf)

Note that tiles are padded at the edge of an image. This requires an image [mask](https://trac.osgeo.org/gdal/wiki/rfc15_nodatabitmask) to be defined if tile sizes do not align with the image width / height (as in the test data which demonstrates this effect).


## Data Preparation

Read the document on [COG](https://trac.osgeo.org/gdal/wiki/CloudOptimizedGeoTIFF) and create a tiled pyramid GeoTIFF.

For example;

```
gdal_translate SENTINEL2_L1C:S2A_MSIL1C_20170102T111442_N0204_R137_T30TXT_20170102T111441.SAFE/MTD_MSIL1C.xml:TCI:EPSG_32630 \
               S2A_MSIL1C_20170102T111442_N0204_R137_T30TXT_20170102T111441_TCI.tif \
               -co TILED=YES -co COMPRESS=DEFLATE
gdaladdo -r average  S2A_MSIL1C_20170102T111442_N0204_R137_T30TXT_20170102T111441_TCI.tif 2 4 8 16 32
gdal_translate S2A_MSIL1C_20170102T111442_N0204_R137_T30TXT_20170102T111441_TCI.tif \
               S2A_MSIL1C_20170102T111442_N0204_R137_T30TXT_20170102T111441_TCI_cloudoptimized_2.tif \
               -co TILED=YES -co COMPRESS=JPEG -co PHOTOMETRIC=YCBCR -co COPY_SRC_OVERVIEWS=YES
```

This library also works with a file hosted in an S3 bucket.

## Installation

`pip install -r requirements.txt`

## Command line interface

```
python -m cogdumper.filedumper --help
python -m cogdumper.httpdumper --help
python -m cogdumper.s3dumper --help
```

e.g.

```
python -m cogdumper.filedumper --file data/cog.tif --xyz 0 0 0
python -m cogdumper.httpdumper --server http://localhost:8080 --path data --resource cog.tif
python -m cogdumper.s3dumper --bucket bucket_name --key key_name/image.tif --xyz 0 0 0
```
