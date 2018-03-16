"""TIFF read exceptions."""

class TIFFError(Exception):
    exit_code = 1

    def __init__(self, message):
        self.message = message

class JPEGError(Exception):
    exit_code = 1

    def __init__(self, message):
        self.message = message
