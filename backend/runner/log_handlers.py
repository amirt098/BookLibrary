import os
import zlib
from logging.handlers import RotatingFileHandler


def my_namer(name):
    return name + ".gz"


def my_rotator(source, dest):
    with open(source, "rb") as sf:
        data = sf.read()
        compressed = zlib.compress(data, 9)
        with open(dest, "wb") as df:
            df.write(compressed)
    os.remove(source)


class CustomGZIPRotator(RotatingFileHandler):

    def __init__(self, *args, **kwargs):
        super(CustomGZIPRotator, self).__init__(*args, **kwargs)
        self.rotator = my_rotator
        self.namer = my_namer
