# Copyright (c) 2019 Delta Foundry, All rights reserved

import warnings
import hashlib
import io


def deprecated(message: str = None):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    def sub(func):
        def proxy_f(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            if message is None:
                ws = f'Call to deprecated function {func.__name__}.'
            else:
                ws = message
            warnings.warn(ws,
                          category=DeprecationWarning,
                          stacklevel=2)
            warnings.simplefilter('default', DeprecationWarning)
            return func(*args, **kwargs)
        return proxy_f
    return sub


def __stream_hash(hashing_algorithm: str, stream: io.BytesIO, restore_pos: bool = True):
    """!!!Please note that this function is not to be used directly!!!
    This function is used internally by other methods in this class however if you still want to use it directly,
    documentation can be found bellow
    Keyword arguments:
    hashing_algorithm -- algorithm to use we recommend using the hashlib.algorithms_available attribute to choose an
    algorithm (default none)
    stream -- a binary stream with read capabilities
    """

    try:
        ha: hash = hashlib.new(hashing_algorithm)
    except ValueError as e:
        raise ValueError(f'Error, inappropriate hashing algorithm, [{e}]')
    else:
        stor_pos = stream.tell()
        stream.seek(0)
        for data in read_chunk(ha.block_size, stream):
            ha.update(data)
        if restore_pos:
            stream.seek(stor_pos)
        return ha.digest()


def read_chunk(chunk_size, stream: io.BytesIO):
    while True:
        data = stream.read(chunk_size)
        if not data:
            break
        yield data