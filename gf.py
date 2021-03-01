import os
import struct


def get_uint32(fb, offset):
    return int.from_bytes(fb[offset:offset+4], byteorder='little')


def get_uint16(fb, offset):
    return int.from_bytes(fb[offset:offset+2], byteorder='little')


def get_int32(fb, offset):
    return int.from_bytes(fb[offset:offset+4], byteorder='little', signed=True)


def get_int16(fb, offset):
    return int.from_bytes(fb[offset:offset+2], byteorder='little', signed=True)


def get_float16(fb, offset):
    flt = int.from_bytes(fb[offset:offset+2], 'little', signed=True)
    flt = flt / (2 ** 15 - 1)
    return flt


def get_float32(fb, offset):
    return struct.unpack('f', fb[offset:offset+4])[0]


def mkdir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

