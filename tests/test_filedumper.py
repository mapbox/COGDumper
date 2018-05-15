"""Tests the filedumper."""

import os

import pytest

from cogdumper.cog_tiles import COGTiff
from cogdumper.errors import TIFFError
from cogdumper.filedumper import Reader as FileReader


@pytest.fixture
def data_dir():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


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


@pytest.fixture
def be_tiff(data_dir):
    f = os.path.join(
        data_dir,
        'be_cog.tif'
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


def test_be_tiff_version(be_tiff):
    reader = FileReader(be_tiff)
    cog = COGTiff(reader.read)
    assert cog.version == 42


def test_tiff_ifds(tiff):
    reader = FileReader(tiff)
    cog = COGTiff(reader.read)
    # read private variable directly for testing
    assert len(cog._image_ifds) > 0
    assert 8 == len(cog._image_ifds[0]['tags'])
    assert 0 == cog._image_ifds[4]['next_offset']


def test_be_tiff_ifds(be_tiff):
    reader = FileReader(be_tiff)
    cog = COGTiff(reader.read)
    # read private variable directly for testing
    assert len(cog._image_ifds) > 0
    assert 8 == len(cog._image_ifds[0]['tags'])
    assert 0 == cog._image_ifds[4]['next_offset']


def test_bigtiff_ifds(bigtiff):
    reader = FileReader(bigtiff)
    cog = COGTiff(reader.read)
    # read private variable directly for testing
    assert len(cog._image_ifds) > 0
    assert 7 == len(cog._image_ifds[0]['tags'])
    assert 0 == cog._image_ifds[4]['next_offset']


def test_tiff_tile(tiff):
    reader = FileReader(tiff)
    cog = COGTiff(reader.read)
    mime_type, tile = cog.get_tile(0, 0, 0)
    assert 1 == len(cog._image_ifds[0]['offsets'])
    assert 1 == len(cog._image_ifds[0]['byte_counts'])
    assert 'jpeg_tables' in cog._image_ifds[0]
    assert 73 == len(cog._image_ifds[0]['jpeg_tables'])
    assert mime_type == 'image/jpeg'

def test_bad_tiff_tile(tiff):
    reader = FileReader(tiff)
    cog = COGTiff(reader.read)
    with pytest.raises(TIFFError) as err:
        cog.get_tile(10, 10, 0)
    with pytest.raises(TIFFError) as err:
        cog.get_tile(10, 10, 10)

def test_bigtiff_tile(bigtiff):
    reader = FileReader(bigtiff)
    cog = COGTiff(reader.read)
    mime_type, tile = cog.get_tile(0, 0, 0)
    assert 1 == len(cog._image_ifds[0]['offsets'])
    assert 1 == len(cog._image_ifds[0]['byte_counts'])
    assert 'jpeg_tables' in cog._image_ifds[0]
    assert cog._image_ifds[0]['jpeg_tables'] is None
    assert mime_type == 'application/octet-stream'
