"""
Augment the base `StringIO` module

AUTHORS:
 - Badi' Abdul-Wahid

CHANGES:
 - 2014-04-02: provide `indent()`, `dedent()`, and `writeln()` methods
"""
import StringIO as stringio
import pdb; pdb.set_trace()

class StringIO(stringio.StringIO):
    def __init__(self, *args, **kws):
        stringio.StringIO.__init__(self, *args, **kws)
        self.indentlvl = 0

    def indent(self, by=4):
        self.indentlvl += by

    def dedent(self, by=4):
        self.indentlvl -= by

    def write(self, *args, **kws):
        stringio.StringIO.write(self, self.indentlvl * ' ')
        stringio.StringIO.write(self, *args, **kws)

    def writeln(self, *args, **kws):
        self.write(*args, **kws)
        stringio.StringIO.write(self, '\n')

