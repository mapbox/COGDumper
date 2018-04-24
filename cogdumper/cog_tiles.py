"""Function for extracting tiff tiles."""

from abc import abstractmethod
from math import ceil
import struct

from cogdumper.errors import TIFFError
from cogdumper.jpegreader import insert_tables
from cogdumper.tifftags import compression as CompressionType
from cogdumper.tifftags import sizes as TIFFSizes
from cogdumper.tifftags import tags as TIFFTags


class AbstractReader:  # pragma: no cover
    @abstractmethod
    def read(offset, len):
        pass


class COGTiff:
    """
    Cloud Optimised GeoTIFF
    -----
    Format
        TIFF / BigTIFF signature
        IFD (Image File Directory) of full resolution image
        Values of TIFF tags that don't fit inline in the IFD directory, such as TileOffsets, TileByteCounts and GeoTIFF keys
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
        """Parses a (Big)TIFF for image tiles.
        Parameters
        ----------
        reader:
            A reader that implements the cogdumper.cog_tiles.AbstractReader methods
        """
        self._init = False
        self._endian = '<'
        self._version = 42
        self.read = reader
        self._big_tiff = False
        self._offset = 0
        self._image_ifds = []
        self._mask_ifds = []

    def ifds(self):
        """Reads TIFF image file directories from a COG recursively.
        Parameters
        -----------
        offset:
            number, offset into the tiff stream to read from, this is only
            required for the first image file directory
        overview:
            number, an identifier that is the overview level in the COG
            image pyramid
        Yield
        --------
        dict: Image File Directory for the next IFD
        """
        while self._offset != 0:
            next_offset = 0
            pos = 0
            tags = []
            if self._big_tiff:
                bytes = self.read(self._offset, 8)
                num_tags = struct.unpack(f'{self._endian}Q', bytes)[0]
                bytes = self.read(self._offset + 8, (num_tags * 20) + 8)

                for t in range(0, num_tags):
                    code = struct.unpack(
                        f'{self._endian}H',
                        bytes[pos: pos + 2]
                    )[0]

                    if code in TIFFTags:
                        dtype = struct.unpack(
                            f'{self._endian}H',
                            bytes[pos + 2: pos + 4]
                        )[0]

                        if dtype not in TIFFSizes:  # pragma: no cover
                            raise TIFFError(f'Unrecognised data type {dtype}')

                        num_values = struct.unpack(
                            f'{self._endian}Q',
                            bytes[pos + 4: pos + 12]
                        )[0]
                        tag_len = num_values * TIFFSizes[dtype]['size']
                        if tag_len <= 8:
                            data = bytes[pos + 12: pos + 12 + tag_len]
                        else:  # pragma: no cover
                            data_offset = struct.unpack(
                                f'{self._endian}Q',
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

                self._offset = self._offset + 8 + pos
                next_offset = struct.unpack(
                    f'{self._endian}Q',
                    self.read(self._offset, 8)
                )[0]
            else:
                bytes = self.read(self._offset, 2)
                num_tags = struct.unpack(f'{self._endian}H', bytes)[0]
                bytes = self.read(self._offset + 2, (num_tags * 12) + 2)
                for t in range(0, num_tags):
                    code = struct.unpack(
                        f'{self._endian}H',
                        bytes[pos: pos + 2]
                    )[0]

                    if code in TIFFTags:
                        dtype = struct.unpack(
                            f'{self._endian}H',
                            bytes[pos + 2: pos + 4]
                        )[0]

                        if dtype not in TIFFSizes:  # pragma: no cover
                            raise TIFFError(f'Unrecognised data type {dtype}')

                        num_values = struct.unpack(
                            f'{self._endian}L',
                            bytes[pos + 4: pos + 8]
                        )[0]
                        tag_len = num_values * TIFFSizes[dtype]['size']
                        if tag_len <= 4:
                            data = bytes[pos + 8: pos + 8 + tag_len]
                        else:
                            data_offset = struct.unpack(
                                f'{self._endian}L',
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

                self._offset = self._offset + 2 + pos
                next_offset = struct.unpack(
                    f'{self._endian}L',
                    self.read(self._offset, 4)
                )[0]

            self._offset = next_offset

            yield {
                'tags': tags,
                'next_offset': next_offset
            }

    def read_header(self):
        # read first 4 bytes to determine tiff or bigtiff and byte order
        bytes = self.read(0, 4)
        if bytes[:2] == b'MM':
            self._endian = '>'

        self._version = struct.unpack(f'{self._endian}H', bytes[2:4])[0]

        if self._version == 42:
            # TIFF
            self._big_tiff = False
            # read offset to first IFD
            self._offset = struct.unpack(f'{self._endian}L', self.read(4, 4))[0]
        elif self._version == 43:
            # BIGTIFF
            self._big_tiff = True
            bytes = self.read(4, 12)
            bytesize = struct.unpack(f'{self._endian}H', bytes[0:2])[0]
            w = struct.unpack(f'{self._endian}H', bytes[2:4])[0]
            self._offset = struct.unpack(f'{self._endian}Q', bytes[4:])[0]
            if bytesize != 8 or w != 0:  # pragma: no cover
                raise TIFFError(f"Invalid BigTIFF with bytesize {bytesize} and word {w}")
        else:  # pragma: no cover
            raise TIFFError(f"Invalid version {self._version} for TIFF file")

        self._init = True

        # for JPEG we need to read all IFDs, they are at the front of the file
        for ifd in self.ifds():
            mime_type = 'image/jpeg'
            # tile offsets are an extension but if they aren't in the file then
            # you can't get a tile back!
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
                        f'{self._endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 257:
                    # image height
                    image_height = struct.unpack(
                        f'{self._endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 259:
                    # compression
                    val = struct.unpack(
                        f'{self._endian}{fmt}',
                        t['data']
                    )[0]
                    if val in CompressionType:
                        mime_type = CompressionType[val]
                    else:
                        mime_type = 'application/octet-stream'
                elif code == 322:
                    # tile width
                    tile_width = struct.unpack(
                        f'{self._endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 323:
                    # tile height
                    tile_height = struct.unpack(
                        f'{self._endian}{fmt}',
                        t['data']
                    )[0]
                elif code == 324:
                    # tile offsets
                    offsets = struct.unpack(
                        f'{self._endian}{t["num_values"]}{fmt}',
                        t['data']
                    )
                elif code == 325:
                    # tile byte counts
                    byte_counts = struct.unpack(
                        f'{self._endian}{t["num_values"]}{fmt}',
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

            if (ifd['compression'] == 'deflate'):
                self._mask_ifds.append(ifd)
            else:
                self._image_ifds.append(ifd)

        if len(self._image_ifds) == 0 and len(self._mask_ifds) > 0:  # pragma: no cover
            self._image_ifds = self._mask_ifds
            self._mask_ifds = []

    def get_tile(self, x, y, z):
        if self._init is False:
            self.read_header()

        if z < len(self._image_ifds):
            image_ifd = self._image_ifds[z]
            idx = (y * image_ifd['ny_tiles']) + x
            if idx > len(image_ifd['offsets']):
                raise TIFFError(f'Tile {x} {y} {z} does not exist')
            else:
                offset = image_ifd['offsets'][idx]
                byte_count = image_ifd['byte_counts'][idx]
                tile = self.read(offset, byte_count)
                if image_ifd['compression'] == 'image/jpeg':
                    # fix up jpeg tile with missing quantization tables
                    tile = insert_tables(tile, image_ifd['jpeg_tables'])
                    # look for a bit mask file
                    if z < len(self._mask_ifds):
                        mask_ifd = self._mask_ifds[z]
                        mask_offset = mask_ifd['offsets'][idx]
                        mask_byte_count = mask_ifd['byte_counts'][idx]
                        mask_tile = self.read(
                            mask_offset,
                            mask_byte_count
                            )
                        tile = tile + mask_tile
                    return image_ifd['compression'], tile
                else:
                    return image_ifd['compression'], tile
        else:
            raise TIFFError(f'Overview {z} is out of bounds.')

    @property
    def version(self):
        if self._init is False:
            self.read_header()
        return self._version
