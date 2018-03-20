"""List of supported tiff tags."""


tags = {
    256: 'ImageWidth',
    257: 'ImageLength',
    322: 'TileWidth',
    323: 'TileLength',
    324: 'TileOffsets',
    325: 'TileByteCounts',
    259: 'Compression',
    347: 'JPEGTables'
}

compression = {
    6: 'image/jpeg',
    7: 'image/jpeg',
    8: 'deflate',
    34712: 'image/jp2'
}

sizes = {
    1: {
        # TIFFByte
        'format': 'B',
        'size': 1
    },
    2: {
        # TIFFascii
        'format': 'c',
        'size': 1
        },
    3: {
        # TIFFshort
        'format': 'H',
        'size': 2
        },
    4: {
        # TIFFlong
        'format': 'L',
        'size': 4
        },
    5: {
        # TIFFrational
        'format': 'f',
        'size': 4
        },
    7: {
        # undefined
        'format': 'B',
        'size': 1
        },
    12: {
        # TIFFdouble
        'format': 'd',
        'size': 8
    },
    16: {
        # TIFFlong8
        'format': 'Q',
        'size': 8
    }
}
