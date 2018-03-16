"""Tests the filedumper."""

import os

import pytest

from cogdumper import (FileReader, COGTiff, TIFFError)


@pytest.fixture
def data_dir():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..',
        'data')


@pytest.fixture
def tiff(data_dir):
    f = os.path.join(
        data_dir,
        'cog.tif'
    )
    with open(f, 'rb') as src:
        yield src


@pytest.fixture
def bigtiff(data_dir):
    f = os.path.join(
        data_dir,
        'BigTIFF.tif'
    )
    with open(f, 'rb') as src:
        yield src

def test_tiff_version(tiff):
    reader = FileReader(tiff)
    cog = COGTiff(reader.read)
    assert cog.version == 42

def test_bigtiff_version(bigtiff):
    reader = FileReader(bigtiff)
    cog = COGTiff(reader.read)
    assert cog.version == 43

def test_tiff_ifds(tiff):
    reader = FileReader(tiff)
    cog = COGTiff(reader.read)
    # read private variable directly for testing
    assert cog._ifds == {}
    cog.read_header()
    assert 0 in cog._ifds
    assert 8 == len(cog._ifds[0]['tags'])
    # read a next overview IFD to test reading is incremental
    cog.read_ifd(1)
    assert [0, 1] == sorted(cog._ifds.keys())
    # skip to test range parsing
    cog.read_ifd(5)
    assert [0, 1, 2, 3, 4, 5] == sorted(cog._ifds.keys())
    assert 0 == cog._ifds[5]['next_offset']
    # check out of range
    with pytest.raises(TIFFError) as tiff_error:
        cog.read_ifd(10)

def test_bigtiff_ifds(bigtiff):
    reader = FileReader(bigtiff)
    cog = COGTiff(reader.read)
    # read private variable directly for testing
    assert cog._ifds == {}
    cog.read_header()
    assert 0 in cog._ifds
    assert 7 == len(cog._ifds[0]['tags'])
    cog.read_ifd(4)
    assert 0 == cog._ifds[4]['next_offset']
    # check out of range
    with pytest.raises(TIFFError) as tiff_error:
        cog.read_ifd(10)

def test_tiff_tile(tiff):
    reader = FileReader(tiff)
    cog = COGTiff(reader.read)
    mime_type, tile = cog.get_tile(0, 0, 0)
    assert 1849 == len(cog._ifds[0]['offsets'])
    assert 1849 == len(cog._ifds[0]['byte_counts'])
    assert 'jpeg_tables' in cog._ifds[0]
    assert 142 == len(cog._ifds[0]['jpeg_tables'])
    assert mime_type == 'image/jpeg'

def test_bigtiff_tile(bigtiff):
    reader = FileReader(bigtiff)
    cog = COGTiff(reader.read)
    mime_type, tile = cog.get_tile(0, 0, 0)
    assert 1 == len(cog._ifds[0]['offsets'])
    assert 1 == len(cog._ifds[0]['byte_counts'])
    assert 'jpeg_tables' in cog._ifds[0]
    assert cog._ifds[0]['jpeg_tables'] is None
    assert mime_type == 'image/tiff'
