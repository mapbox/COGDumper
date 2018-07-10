"""A utility to dump tiles directly from a tiff file in an S3 bucket."""

import os
import logging

import boto3

from cogdumper.cog_tiles import AbstractReader

logger = logging.getLogger(__name__)

region = os.environ.get('AWS_REGION', 'us-east-1')
s3 = boto3.resource('s3', region_name=region)


class Reader(AbstractReader):
    """Wraps the remote COG."""

    def __init__(self, bucket_name, key):
        """Init reader object."""
        self.bucket = bucket_name
        self.key = key
        self.source = s3.Object(self.bucket, self.key)

    def read(self, offset, length):
        """Read method."""
        start = offset
        stop = offset + length - 1
        logger.info(f'Reading bytes: {start} to {stop}')
        r = self.source.get(Range=f'bytes={start}-{stop}')
        return r['Body'].read()
