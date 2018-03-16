"""Simple JPEG reader for inserting missing markers."""

from cogdumper.errors import JPEGError


SOI = 0xd8

def insert_tables(data, tables):
    if tables:
        if data[0] == 0xFF and data[1] == SOI:
            # insert tables, first removing the SOI and EOI
            return data[0:2] + tables[2:-2] + data[2:]
        else:
            raise JPEGError('Missing SOI marker for JPEG tile')
    else:
        # no-op as per the spec, segment contains all of the JPEG data required
        return data
