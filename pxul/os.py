"""
Augment the base `os` module.

AUTHORS:
 - Badi' Abdul-Wahid

CHANGES:
 - 2013-04-02:
     - Add `StackDir`
     - Add `ensure_dir`
     - Add `ensure_file`
"""

import os


class StackDir(object):
    """
    Temporarily enter a directory before return the the current one.
    Mainly intended to be used as a resource using the `with` statement:
    >>> with StackDir('/tmp/'):
    ...    print os.getcwd()
    """
    def __init__(self, path):
        self.dst = path
        self.src = os.path.abspath(os.getcwd())

    def __enter__(self):
        ensure_dir(self.dst)
        os.chdir(self.dst)

    def __exit__(self, *args, **kws):
        os.chdir(self.src)

    def enter(self):
        """
        Enter the alternate directory.
        """
        self.__enter__()

    def exit(self):
        """
        Exit the alternate directory
        """
        self.__exit__()

def ensure_dir(path):
    """
    Make sure the `path` if a directory by creating it if needed.
    """
    if not os.path.exists(path):
        os.makedirs(path)

def ensure_file(path):
    """
    Make sure the `path` is a file by creating it if needed.
    """
    if os.path.exists(path): return
    root = os.path.dirname(path)
    ensure_dir(root)
    open(path, 'w').close()
