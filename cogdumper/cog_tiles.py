"""Function for extracting tiff tiles."""

from abc import abstractmethod
import struct
from math import ceil

from cogdumper.errors import TIFFError
from cogdumper.tifftags import compression as CompressionType
from cogdumper.tifftags import sizes as TIFFSizes
from cogdumper.tifftags import tags as TIFFTags
from cogdumper.jpegreader import insert_tables

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo('Version 1.0')
    ctx.exit()

class AbstractReader:
    @abstractmethod
    def read(offset, len):
        pass

class COGTiff:
    """
    Cloud Optimised GeoTIFF
    -----
    Format

        TIFF / BigTIFF signature
        IFD (​Image File Directory) of full resolution image
        Values of TIFF tags that don't fit inline in the IFD directory, such as TileOffsets?, TileByteCounts? and GeoTIFF keys
        Optional: IFD (Image File Directory) of first overview (typically subsampled by a factor of 2), followed by the values of its tags that don't fit inline
        Optional: IFD (Image File Directory) of second overview (typically subsampled by a factor of 4), followed by the values of its tags that don't fit inline
        ...
        Optional: IFD (Image File Directory) of last overview (typically subsampled by a factor of 2N), followed by the values of its tags that don't fit inline
        Optional: tile content of last overview level
        ...
        Optional: tile content of first overview level
        Tile content of full resolution image.
    """
    def __init__(self, reader):
        self.init = False
        self.endian = '<'
        self._version = 42
        self.read = reader
        self.big_tiff = False
        self._ifds = {}

    def read_ifd(self, overview, offset=None):
        """Reads TIFF image file directories from a COG recursively.

        Parameters
        -----------

        offset:
            number, offset into the tiff stream to read from, this is only
            required for the first image file directory
        overview:
            number, an identifier that is the overview level in the COG
            image pyramid

        Returns
        --------
        dict: Image File Directory for requested overview image
        """
        if self.init == False:
            self.read_header()

        overviews = sorted(self._ifds.keys())

        if overview >= len(overviews):
            if overview == 0:
                last_overview = -1
            else:
                last_overview = overviews[-1]
                if self._ifds[last_overview]['next_offset'] == 0:
                    raise TIFFError(f'Request overview {overview} not found')

            if overview > 0 and offset is None:
                last_ifd = self._ifds[last_overview]
                offset = last_ifd['next_offset']
            elif overview > 0:
                raise TIFFError('Specifying an overview > 0 '
                                'and an offset is not supported.'
                                )

            for i in range(last_overview + 1, overview + 1):
                next_offset = 0
                pos = 0
                tags = []
                if self.big_tiff:
                    bytes = self.read(offset, 8)
                    num_tags = struct.unpack(f'{self.endian}Q', bytes)[0]
                    bytes = self.read(offset + 8, (num_tags * 20) + 8)

                    for t in range(0, num_tags):
                        code = struct.unpack(
                            f'{self.endian}H',
                            bytes[pos: pos + 2]
                        )[0]

                        if code in TIFFTags:
                            dtype =  struct.unpack(
                                f'{self.endian}H',
                                bytes[pos + 2: pos + 4]
                            )[0]

                            if dtype not in TIFFSizes:
                                raise TIFFError(
                                    f'Unrecognised data type {dtype}'
                                )

                            num_values = struct.unpack(
                                f'{self.endian}Q',
                                bytes[pos + 4: pos + 12]
                            )[0]
                            tag_len = num_values * TIFFSizes[dtype]['size']
                            if tag_len <= 8:
                                data = bytes[pos + 12: pos + 12 + tag_len]
                            else:
                                data_offset = struct.unpack(
                                    f'{self.endian}Q',
                                    bytes[pos + 12: pos + 20]
                                )[0]
                                data = self.read(data_offset, tag_len)

                            tags.append(
                                {
                                    'code': code,
                                    'dtype': TIFFSizes[dtype],
                                    'num_values': num_values,
                                    'data': data
                                }
                            )

                        pos = pos + 20

                    offset = offset + 8 + pos
                    next_offset = struct.unpack(
                        f'{self.endian}Q',
                        self.read(offset, 8)
                    )[0]
                else:
                    bytes = self.read(offset, 2)
                    num_tags = struct.unpack(f'{self.endian}H', bytes)[0]
                    bytes = self.read(offset + 2, (num_tags * 12) + 2)
                    for t in range(0, num_tags):
                        code = struct.unpack(
                            f'{self.endian}H',
                            bytes[pos: pos + 2]
                        )[0]

                        if code in TIFFTags:
                            dtype =  struct.unpack(
                                f'{self.endian}H',
                                bytes[pos + 2: pos + 4]
                            )[0]

                            if dtype not in TIFFSizes:
                                raise TIFFError(
                                    f'Unrecognised data type {dtype}'
                                )

                            num_values = struct.unpack(
                                f'{self.endian}L',
                                bytes[pos + 4: pos + 8]
                            )[0]
                            tag_len = num_values * TIFFSizes[dtype]['size']
                            if tag_len <= 4:
                                data = bytes[pos + 8: pos + 8 + tag_len]
                            else:
                                data_offset = struct.unpack(
                                    f'{self.endian}L',
                                    bytes[pos + 8: pos + 12]
                                )[0]
                                data = self.read(data_offset, tag_len)

                            tags.append(
                                {
                                    'code': code,
                                    'dtype': TIFFSizes[dtype],
                                    'num_values': num_values,
                                    'data': data
                                }
                            )

                        pos = pos + 12

                    offset = offset + 2 + pos
                    next_offset = struct.unpack(
                        f'{self.endian}L',
                        self.read(offset, 4)
                    )[0]

                self._ifds[i] = {
                    'tags': tags,
                    'next_offset': next_offset
                }

                offset = next_offset

                if next_offset == 0 and i < overview:
                    raise TIFFError(f'Request overview {overview} not found')

        return self._ifds[overview]

    def read_header(self):
        # read first 4 bytes to determine tiff or bigtiff and byte order
        bytes = self.read(0, 4)
        if bytes[:2] == b'MM':
            self.endian = '>'

        self._version = struct.unpack(f'{self.endian}H', bytes[2:4])[0]

        if self._version == 42:
            # TIFF
            self.big_tiff = False
            # read offset to first IFD
            offset = struct.unpack(f'{self.endian}L', self.read(4, 4))[0]
        elif self._version == 43:
            # BIGTIFF
            self.big_tiff = True
            bytes = self.read(4, 12)
            bytesize = struct.unpack(f'{self.endian}H', bytes[0:2])[0]
            w = struct.unpack(f'{self.endian}H', bytes[2:4])[0]
            offset = struct.unpack(f'{self.endian}Q', bytes[4:])[0]
            if bytesize != 8 or w != 0:
                raise TIFFError(f"Invalid BigTIFF with bytesize {bytesize} and word {w}")
        else:
            raise TIFFError(f"Invalid version {self._version} for TIFF file")

        # read ifd for main header
        self.init = True
        self.read_ifd(0, offset=offset)

    def get_tile(self, x, y, z):
        ifd = self.read_ifd(z)
        mime_type = 'image/jpeg'
        # tile offsets are an extension but if they aren't in the file then
        # you can't get a tile back!
        if 'offsets' not in ifd:
            offsets = []
            byte_counts = []
            image_width = 0
            image_height = 0
            tile_width = 0
            tile_height = 0
            jpeg_tables = None

            for t in ifd['tags']:
                code = t['code']
                fmt = t['dtype']['format']
                if code == 256:
                    # image width
                    image_width = struct.unpack(
                        f'{self.endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 257:
                    # image height
                    image_height = struct.unpack(
                        f'{self.endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 259:
                    # compression
                    val = struct.unpack(
                        f'{self.endian}{fmt}',
                        t['data']
                    )[0]
                    if val in CompressionType:
                        mime_type = CompressionType[val]
                    else:
                        mime_type = 'image/tiff'
                elif code == 322:
                    # tile width
                    tile_width = struct.unpack(
                        f'{self.endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 323:
                    # tile height
                    tile_height = struct.unpack(
                        f'{self.endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 324:
                    # tile offsets
                    offsets = struct.unpack(
                        f'{self.endian}{t["num_values"]}{fmt}',
                        t['data']
                    )
                elif code == 325:
                    # tile byte counts
                    byte_counts = struct.unpack(
                        f'{self.endian}{t["num_values"]}{fmt}',
                        t['data']
                    )
                elif code == 347:
                    # JPEG Tables
                    jpeg_tables = t['data']

            if len(offsets) == 0:
                raise TIFFError('TIFF Tiles are not found in IFD {z}')

            ifd['image_width'] = image_width
            ifd['image_height'] = image_height
            ifd['compression'] = mime_type
            ifd['tile_width'] = tile_width
            ifd['tile_height'] = tile_height
            ifd['offsets'] = offsets
            ifd['byte_counts'] = byte_counts
            ifd['jpeg_tables'] = jpeg_tables

            ifd['nx_tiles'] = ceil(image_width / float(tile_width))
            ifd['ny_tiles'] = ceil(image_height / float(tile_height))

        # retrieve tile
        idx = (y * ifd['ny_tiles']) + (x * ifd['nx_tiles'])
        if idx > len(ifd['offsets']):
            raise TIFFError(f'Tile {x} {y} {z} does not exist')
        else:
            offset = ifd['offsets'][idx]
            byte_count = ifd['byte_counts'][idx]
            tile = self.read(offset, byte_count)
            if ifd['compression'] == 'image/jpeg':
                # fix up jpeg tile with missing quantization tables
                tile = insert_tables(tile, ifd['jpeg_tables'])
                return ifd['compression'], tile
            else:
                return ifd['compression'], tile

    @property
    def version(self):
        if self.init == False:
            self.read_header()
        return self._version
