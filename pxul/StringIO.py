"""
Augment the base `StringIO` module

AUTHORS:
 - Badi' Abdul-Wahid

CHANGES:
 - 2014-04-02: provide `indent()`, `dedent()`, and `writeln()` methods


USAGE:
>>> from pxul.StringIO import StringIO
>>> sio = StringIO()
>>> sio.writeln('hello')
"""
from __future__ import absolute_import
import StringIO as stringio

class StringIO(stringio.StringIO):
    __doc__ = stringio.StringIO.__doc__

    def __init__(self, *args, **kws):
        stringio.StringIO.__init__(self, *args, **kws)
        self.indentlvl = 0
        self._wrote_newline = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def indent(self, by=4):
        """Increase the indentation level"""
        self.indentlvl += by

    def dedent(self, by=4):
        """Decrease the indentation level"""
        self.indentlvl -= by

    def _write(self, string):
        if '\n' in string:
            self._wrote_newline = True
        else:
            self._wrote_newline = False
        stringio.StringIO.write(self, string)

    def write_indented(self, s):
        """Write a string prefixed by `self.indentlvl` spaces"""
        self._write(self.indentlvl * ' ')
        self._write(s)

    def write(self, s):
        """Write a string"""
        if self._wrote_newline:
            self._write(s)
        else:
            self.write_indented(s)

    def writeln(self, s):
        """Write a string followed by a newline"""
        self.write(s)
        stringio.StringIO.write(self, '\n')
