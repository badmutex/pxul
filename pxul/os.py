"""
Augment the base `os` module.

AUTHORS:
 - Badi' Abdul-Wahid

CHANGES:
 - 2013-04-02:
     - Add `StackDir`
     - Add `ensure_dir`
     - Add `ensure_file`
     - Add `find_in_path`
     - Add `find_in_root`
     - Add `SetEnv`
"""
from __future__ import absolute_import
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

class SetEnv(object):
    """
    Set the environment variables in `os.environ`.

    >>> with SetEnv(PATH='/foo/bar/bin', SPAM='eggs'):
    ...   print os.environ['PATH']
    ...   print os.environ['SPAM']
    /foo/bar/bin
    eggs
    """
    def __init__(self, **env):
        self._new_env = env
        self._old_env = dict()

    def __enter__(self):
        for name, value in self._new_env.iteritems():
            value = str(value)
            if name in os.environ:
                self._old_env[name] = os.environ[name]
            os.environ[name] = value
        return self

    def __exit__(self, typ, value, traceback):
        for name, value in self._new_env.iteritems():
            if name in self._old_env:
                os.environ[name] = self._old_env[name]
            else:
                del os.environ[name]

    def set(self):
        """
        Set the environment
        """
        self.__enter__()

    def unset(self):
        """
        Undo the changes to the environment
        """
        self.__exit__()

def clear_dir(dirpath):
    """
    Recursively delete everything under `dirpath`
    """
    for name in glob.iglob(os.path.join(path, '*')):
        if os.path.isdir(name):
            clear_dir(name)
            remove = os.rmdir
        else:
            remove = os.unlink
        logger.info2('Deleting', name)
        remove(name)

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


def find_in_path(exe, search=None):
    """
    Attempts to locate the given executable in the provided search paths.
    If `search` is none the PATH environment variable is searched.

    Params:
     exe :: <str> = executable name
     search :: <list of str> = search paths

    Returns:
     Either None or full path :: <str>
    """

    search = search if search is not None else os.environ['PATH'].split(os.pathsep)
    for prefix in search:
        path = os.path.join(prefix, exe)
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path

def find_in_root(exe, root='/'):
    """
    Attempts to find the executable name by traversing the directory structure starting at `root`

    Params:
     exe :: <str> = executable name
     root :: <str> = prefix to search under

    Returns:
      Either None or path :: <str>
    """
    for dirpath, dirnames, filenames in os.walk(root):
        path = os.path.join(dirpath, exe)
        if exe in filenames and os.access(path, os.X_OK):
            return path
