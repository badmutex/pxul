"""
Augment the base `os` module.

AUTHORS:
 - Badi' Abdul-Wahid

CHANGES:
 - 2015-06-11:
     - rename clear_dir to remove_children (issue #16)
 - 2015-06-09:
     - rename StackDir to in_dir (issue #4)
     - rename TmpDir to tmpdir (issue #5)
     - return the path to the `as` keyword (issue #12)
 - 2015-06-07:
     - Add `fullpath`
     - `ensure_file` should use `fullpath`
 - 2014-08-19:
     - Cleanup, update documentation
     - Add `TmpDir`
 - 2014-07-25:
     - Add `clear_dir`
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
import glob
import shutil
import tempfile


class tmpdir(object):
    """Create a temprorary directory to work in.  This is intended to be
    used as part of a `with`-statement, where entering the context
    creates the directory. All statements executing within the context
    begin in the temporary directory. Exiting the context restores the
    original working directory and removes the temporary directory and
    its contents.

    >>> with tmpdir() as tmppath:
    ...   print tmppath == os.getcwd()
    True
    >>> print tmppath == os.getcwd()
    False
    >>> print os.path.exists(tmppath)
    False

    Accepts the same arguments as :func:`tempfile.mkdtemp`

    """

    def __init__(self, *args, **kws):
        "Accepts the same arguments as :func:`tempfile.mkdtemp`"

        self._d = tempfile.mkdtemp(*args, **kws)
        self._sd = in_dir(self._d)

    def __enter__(self):
        return self._sd.enter()

    def __exit__(self, *args, **kws):
        self._sd.exit()
        shutil.rmtree(self._d)


class in_dir(object):
    """
    Temporarily enter a directory before return the the current one.
    If the directory does not exist it will be created.
    Mainly intended to be used as a resource using the `with` statement:

    >>> with in_dir('/tmp/'):
    ...   print os.getcwd()
    """
    def __init__(self, path):
        self.dst = path
        self.src = os.path.abspath(os.getcwd())

    def __enter__(self):
        ensure_dir(self.dst)
        os.chdir(self.dst)
        return os.getcwd()

    def __exit__(self, *args, **kws):
        os.chdir(self.src)

    def enter(self):
        """
        Enter the alternate directory.
        """
        return self.__enter__()

    def exit(self):
        """
        Exit the alternate directory
        """
        self.__exit__()


class env(object):
    """
    Set the environment variables in `os.environ`.

    .. warning::
       This will **update** a variable that already exists

    >>> with env(PATH='/foo/bar/bin', SPAM='eggs'):
    ...   print os.environ['PATH']
    ...   print os.environ['SPAM']
    /foo/bar/bin
    eggs

    Alternatively

    >>> newenv = env(SPAM='eggs')
    >>> newenv.activate()
    >>> # do something
    >>> newenv.deactivate()
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

    def __exit__(self, *args, **kwargs):
        for name, value in self._new_env.iteritems():
            if name in self._old_env:
                os.environ[name] = self._old_env[name]
            else:
                del os.environ[name]

    def activate(self):
        """
        Set the environment
        """
        self.__enter__()

    def deactivate(self):
        """
        Undo the changes to the environment
        """
        self.__exit__()


def remove_children(dirpath):
    """
    Recursively delete everything under `dirpath`
    """
    for name in glob.iglob(os.path.join(dirpath, '*')):
        if os.path.isdir(name):
            remove_children(name)
            remove = os.rmdir
        else:
            remove = os.unlink
        remove(name)


def fullpath(path):
    """
    Get the absolute path, expanding any variables
    """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


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
    if os.path.exists(path):
        return
    root = os.path.dirname(fullpath(path))
    ensure_dir(root)
    open(path, 'w').close()


def find_in_path(exe, search=None):
    """Attempts to locate the given executable in the provided search
    paths. If `search` is ``None``, then the ``PATH`` environment
    variables is used.

    :param str exe: the executable name
    :param list of str search: search paths
    :returns: the full path to the executable
    :rtype: :class:`None` or :class:`str`
    """
    search = search \
        if search is not None\
        else os.environ['PATH'].split(os.pathsep)

    for prefix in search:
        path = os.path.join(prefix, exe)
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path


def find_in_root(exe, root='/'):
    """Attempts to find the executable name by traversing the directory
    structure starting at `root`.

    :param str exe: executable name
    :param str root: prefix to start the search from
    :returns: full path to the executable
    :rtype: :class:`None` or :class:`str`
    """
    for dirpath, dirnames, filenames in os.walk(root):
        path = os.path.join(dirpath, exe)
        if exe in filenames and os.access(path, os.X_OK):
            return path
