import pxul.StringIO

from unittest import TestCase

import hypothesis.strategies as st
from hypothesis import given


class StringIO_Test(TestCase):

    @given(st.text())
    def test_context_enter(self, s):
        "Entering the StringIO context should be possible"

        with pxul.StringIO.StringIO(s) as ref:
            self.assertEqual(ref.getvalue(), s)

    @given(st.text())
    def test_context_exit(self, s):
        "Accessing the ref outside the context should be an error"

        with pxul.StringIO.StringIO(s) as ref:
            pass

        with self.assertRaises(ValueError):
            ref.getvalue()

        with self.assertRaises(ValueError):
            ref.indent()

        with self.assertRaises(ValueError):
            ref.dedent()

        with self.assertRaises(ValueError):
            ref.write('world')

    def test_indent_default(self):
        "Should indent by default level"
        with pxul.StringIO.StringIO() as ref:
            self.assertEqual(ref.indentlvl, 0)
            ref.indent()
            self.assertEqual(ref.indentlvl, 4)
            ref.writeln('')
            s = ref.getvalue()
            self.assertEqual(s, 4*' '+'\n')

    def test_dedent_default(self):
        "Should dedent if possible"
        with pxul.StringIO.StringIO() as ref:
            self.assertEqual(ref.indentlvl, 0)
            ref.dedent()
            self.assertEqual(ref.indentlvl, 0)
            ref.indent()

    @given(st.text())
    def test_write(self, s):
        "ref.write('foo') should equal 'foo'"
        with pxul.StringIO.StringIO() as ref:
            ref.write(s)
            s2 = ref.getvalue()
            self.assertEqual(s, s2)

    @given(st.text())
    def test_writeln(self, s):
        "ref.write(string) should equal string + '\\n'"
        with pxul.StringIO.StringIO() as ref:
            ref.writeln(s)
            s2 = ref.getvalue()
            self.assertEqual(s + '\n', s2)
