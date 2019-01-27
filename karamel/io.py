# Copyright (c) 2019 Delta Foundry, All rights reserved
import io
from typing import Tuple, TextIO
import os
import platform
import datetime
import karamel.kore


class ChunkIO:
    """ Read data in chunks of a size determined by the buffer size and return it raw or give a callback function
    """

    def __init__(self, stream: io.BytesIO, buff_size: int, ret_to_origin: bool = False,
                 use_callback=False, callback=None, zero_in: bool = True):
        """
        :param stream: The stream to read the chunks from must be binary
        :param buff_size: The size of the reading buffer
        :param ret_to_origin: if the stream should be returned to it's position prior to use by this class
        :param use_callback: if a callback function is to be called with the buffer as the sole parameter if False the
                            read function will return the buffer
        :param callback: the function referred by the previous argument
        :exception OSError: Raised if ret_to_origin is True and the stream is not RA'able
        """
        self._stream = stream
        self.buff_size = buff_size
        self.ret_to_o = ret_to_origin
        self.use_callback = use_callback if callback is not None else False
        self.callback_f = callback
        self.buffer = [self.buff_size]
        self.stream_o_pos = self._stream.tell()
        # If the stream is not seekable and ret_to_origin is True there is a
        # problem as it wont be able to seek to the position it had before being manipulated by this class
        self._seekable = self._stream.seekable()
        self._zero_in = zero_in
        if self.ret_to_o and self._zero_in and not self._seekable:
            raise OSError('Can not return a non RA stream to origin') # As per the previous comment raise an exception

    def __enter__(self): return self


class File:
    """ Describes a file and allows for the application of useful functions.
    This class describes a file with useful information like permissions size and other features
    like the ability to easily hide a file OS independently (for the most common OS's).
    """

    hash: Tuple[bytes, str]

    def __init__(self, path: str, open_stream: bool = False, mode: str = 'rb', cache_hash: bool = True,
                 lock: bool = True):
        """ Constructor of the File class
        :arg path: -- the path to create a File instance with
        :arg open_stream: -- Shall a stream be opened?
        :arg mode: -- if open_stream is true pass a mode with this argument
        """
        if not os.path.exists(path):
            raise IOError(f'File {path} not found')
        self.__file_path = path
        self.__stream = None
        self.__mode = mode
        self.has_open_stream = False
        self.lock = lock
        self.size = os.path.getsize(self.__file_path)
        self.mod_date = os.path.getmtime(self.__file_path)
        self.create_date = self.creation_date()
        self.human_mod_date = datetime.datetime.fromtimestamp(self.mod_date).isoformat()
        """Hash is a tuple with the bytes object on 0 and the hex string on 1"""
        self.hash = None
        if open_stream:
            try:
                self.__stream__ = open(self.__file_path, self.__mode)
            except IOError as e:
                raise EnvironmentError(f'An IO exception has occurred [{e}]')
            else:
                self.has_open_stream = True
        if cache_hash and open_stream:
            self.hash = self.get_hash()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.has_open_stream:
            self.__stream__.close()
            self.has_open_stream = False

    def change_mode(self, mode):
        if self.has_open_stream:
            self.__stream__.close()
            self.__stream__ = open(self.__file_path, mode)
        else:
            raise ValueError('There is not an open stream yet for this file')

    def creation_date(self):
        """
        Try to get the date that a file was created, falling back to when it was
        last modified if that isn't possible.
        """
        if platform.system() == 'Windows':
            return os.path.getctime(self.__file_path)
        else:
            stat = os.stat(self.__file_path)
            try:
                return stat.st_ctime
            except AttributeError:
                # Probably on Linux. No easy way to get creation dates,
                # so we'll settle for when its content was last modified.
                return stat.st_mtime

    def get_hash(self):
        if self.has_open_stream:
            return karamel.kore.stream_sha256_hash(self.__stream)
        else:
            raise EnvironmentError('No open stream to retrieve data from')

    def get_descriptor(self): return self.__file_path, self.mod_date, self.human_mod_date, self.create_date,\
        self.has_open_stream, self
