import pxul.command

from unittest import TestCase
import copy


class call_Test(TestCase):
    def test_cmd_is_str(self):
        "Should throw an exception if the command is a naked string"
        cmd = 'ls'
        with self.assertRaises(pxul.command.ArgumentsError):
            pxul.command.call(cmd)

    def test_returns_triple(self):
        "Should return a triple (out, err, retcode)"
        cmd = 'ls'
        out, err, ret = pxul.command.call([cmd],
                                          stdout=pxul.command.PIPE,
                                          stderr=pxul.command.PIPE)
        self.assertIsNotNone(out)
        self.assertIsNotNone(err)
        self.assertIsNotNone(ret)
        self.assertEqual(ret, 0)


class Command_Test(TestCase):
    def test_init_check(self):
        "Should throw if command is malformed"
        c = 'ls'
        with self.assertRaises(pxul.command.ArgumentsError):
            pxul.command.Command(c)

    def test_init_list1(self):
        "Should create a Command from a one-element list"
        c = ['ls']
        cmd = pxul.command.Command(c)
        self.assertListEqual(cmd.cmd, c)

    def test_init_listN(self):
        "Should create a Command of an n-element list"
        c = ['echo'] + [str(i) for i in xrange(10)]
        cmd = pxul.command.Command(c)
        self.assertListEqual(cmd.cmd, c)

    def test_call_no_args(self):
        "Call with no arguments"
        echo = pxul.command.Command(['echo'], capture='both')
        out, err, ret = echo()
        self.assertEqual(out.strip(), '')
        self.assertEqual(err.strip(), '')
        self.assertEqual(ret, 0)

    def test_call_with_args(self):
        "Call with arguments"
        echo = pxul.command.Command(['echo'], capture='both')
        out, err, ret = echo('hello', 'world')
        self.assertEqual(out.strip(), 'hello world')

    def test_object_immutable(self):
        "__call__ should not modify the state of the object"
        echo = pxul.command.Command(['echo'], silent=True)
        original = copy.deepcopy(echo.__dict__)
        echo('hello', 'world')
        self.assertDictEqual(original, echo.__dict__)
