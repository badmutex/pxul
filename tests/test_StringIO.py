import pxul.StringIO

from unittest import TestCase


class StringIO_Test(TestCase):
    def test_context_enter(self):
        "Entering the StringIO context should be possible"

        s = 'hello'
        with pxul.StringIO.StringIO(s) as ref:
            self.assertEqual(ref.getvalue(), s)

    def test_context_exit(self):
        "Accessing the ref outside the context should be an error"

        s = 'hello'
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

