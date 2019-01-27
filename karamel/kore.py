# Copyright (c) 2019 Delta Foundry, All rights reserved

import ntpath
import os
import platform
import subprocess
import io
import karamel.util


def hide_file(path):
    """
    Simply hides a file if in windows add the hidden attribute if in linux prepend the filename with a .
    """

    if platform.system() == 'Windows':
        subprocess.check_call(["attrib", "+H", path])
    else:
        path_parts = split_path(path)
        os.rename(path_parts[1], f'.{path_parts[1]}')


def split_path(path):
    return ntpath.split(path)


def write_chunk(chunks, file_desc):
        for data in chunks:
            file_desc.write(data)


@karamel.util.deprecated('This function is here for compatibility purposes only as MD5 shall be avoided if possible')
def stream_md5_hash(stream: io.BytesIO):
    """
    Deprecated:
    This function is here for compatibility purposes only as MD5 shall be avoided if possible
    """
    h = karamel.util.__stream_hash('md5', stream)
    return h.hex()


def stream_sha256_hash(stream: io.BytesIO):
    """
    Use this function for most cases as for file hashing SHA256 is the recommended nowadays
    """
    h = karamel.util.__stream_hash('sha256', stream)
    return h, h.hex()


def rang(lower, n, upper): return lower < n < upper


def rang_i(lower, n, upper): return lower <= n <= upper


if __name__ == '__main__':
    raise RuntimeError('this file is a module and should not be ran directly')


