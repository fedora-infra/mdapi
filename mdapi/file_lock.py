# -*- coding: utf-8 -*-
#
# Copyright © derpston.
#
# Source: https://github.com/derpston/python-simpleflock/
#
# License: WTFPL
#

'''
Simple file lock mechanism
'''

import time
import os
import fcntl
import errno


class FileFlock:
    """ Provides the simplest possible interface to flock-based file locking.
    Intended for use with the `with` syntax. It will create/truncate/delete
    the lock file as necessary.

    """

    def __init__(self, path, timeout=None, wait_for=0.1):
        self._path = path
        self._timeout = timeout
        self._fd = None
        self.wait_for = wait_for

    def __enter__(self):
        self._fd = os.open(self._path, os.O_CREAT)
        start_lock_search = time.time()
        while True:
            try:
                fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                # Lock acquired!
                return
            except IOError as ex:
                # Keep going if resource temporarily unavailable
                if ex.errno != errno.EAGAIN:
                    raise
                # Exceeded the user-specified timeout.
                elif self._timeout is not None \
                        and time.time() > (start_lock_search + self._timeout):
                    raise

            # Let's not spin continuously
            time.sleep(self.wait_for)

    def __exit__(self, *args):
        fcntl.flock(self._fd, fcntl.LOCK_UN)
        os.close(self._fd)
        self._fd = None

        # Try to remove the lock file, but don't try too hard because it is
        # unnecessary. This is mostly to help the user see whether a lock
        # exists by examining the filesystem.
        try:
            os.unlink(self._path)
        except:
            pass
