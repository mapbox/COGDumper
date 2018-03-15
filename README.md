# COG Dumper

A python3 utility to extract the tile from a Cloud Optimized GeoTIFF (COG) without decompressing the contained data. Tiff data can be hosted locally, on a web server or S3.

This can be useful for serving WebP/JPEG compressed tiles from a TIFF without invoking Rasterio and GDAL.

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

This library works with a file hosted in an S3 bucket.

## Installation

`pip install -r requirements.txt`

## Command line interface

```
python cogdumper/filedumper.py --help
python cogdumper/httpdumper.py --help
python cogdumper/s3dumper.py --help
```

e.g.

```
python cogdumper/filedumper.py --file data/cog.tif --output out --xyz 0 0 0
```
