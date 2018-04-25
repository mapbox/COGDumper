# COG Dumper

[![Build Status](https://travis-ci.org/mapbox/COGDumper.svg?branch=master)](https://travis-ci.org/mapbox/COGDumper) [![codecov](https://codecov.io/gh/mapbox/COGDumper/branch/master/graph/badge.svg?token=Yd3y5aTvGo)](https://codecov.io/gh/mapbox/COGDumper)

A python (3.6) utility to extract a tile from a Cloud Optimized GeoTIFF (COG) without decompressing the contained data. Tiff data can be hosted locally, on a web server or S3.

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

Python 3.6 is required.

```
pip install cogdumper
```

or from source

```
git clone https://github.com/mapbox/COGDumper
cd COGDumper
pip install .
```

## Command line interface

```
$ cogdumper --help
Usage: cogdumper [OPTIONS] COMMAND [ARGS]...

  Command line interface for COGDumper.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  file  COGDumper cli for local dataset.
  http  COGDumper cli for web hosted dataset.
  s3    COGDumper cli for AWS S3 hosted dataset
```

##### local files
```
cogdumper file --help
Usage: cogdumper file [OPTIONS]

  COGDumper cli for local dataset.

Options:
  --file PATH       input file  [required]
  --output PATH     local output directory
  --xyz INTEGER...  xyz tile coordinate where z is the overview level
  --version         Show the version and exit.
  --help            Show this message and exit.
```
e.g. `cogdumper file --file data/cog.tif --xyz 0 0 0`

##### web files

```
cogdumper http --help
Usage: cogdumper http [OPTIONS]

  COGDumper cli for web hosted dataset.

Options:
  --server TEXT       server e.g. http://localhost:8080  [required]
  --path TEXT         server path
  --resource TEXT     server resource
  --output DIRECTORY  local output directory
  --xyz INTEGER...    xyz tile coordinates where z is the overview level
  --version           Show the version and exit.
  --help              Show this message and exit.
```

e.g. `cogdumper http --server http://localhost:8080 --path data --resource cog.tif`

##### S3 files
```
cogdumper s3 --help
Usage: cogdumper s3 [OPTIONS]

  COGDumper cli for AWS S3 hosted dataset

Options:
  --bucket TEXT       AWS S3 bucket  [required]
  --key TEXT          AWS S3 key  [required]
  --output DIRECTORY  local output directory
  --xyz INTEGER...    xyz tile coordinates where z is the overview level
  --help              Show this message and exit.
```

e.g. `cogdumper s3 --bucket bucket_name --key key_name/image.tif --xyz 0 0 0`
