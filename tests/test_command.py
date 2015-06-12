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

    def test_returns_namedtuple(self):
        "Result should be a named tuple"
        result = pxul.command.call(['echo', 'hello', 'world'],
                                   stdout=pxul.command.PIPE,
                                   stderr=pxul.command.PIPE)
        self.assertIsInstance(result, pxul.command.Result)
        self.assertEqual(result.out.strip(), 'hello world')
        self.assertEqual(result.err.strip(), '')
        self.assertEqual(result.ret, 0)


class run_Test(TestCase):
    def test_default_ok(self):
        "Default configuration should work with good input"
        res = pxul.command.run(['echo', 'hello'])
        self.assertIsNone(res.out)
        self.assertIsNone(res.err)
        self.assertEqual(res.ret, 0)

    def test_default_bad(self):
        "Default configuration should raise an error on bad input"
        with self.assertRaises(pxul.command.ArgumentsError):
            pxul.command.run('echo bad')

    def test_capture_stdin(self):
        "Should capture the stdout"
        res = pxul.command.run(['echo', 'hello'], capture='stdout')
        self.assertEqual(res.out.strip(), 'hello')

    def test_capture_stdout(self):
        "Should capture the stderr"
        res = pxul.command.run(['echo', 'hello'], capture='stderr')
        self.assertEqual(res.err.strip(), '')

    def test_capture_both(self):
        "Should capture both stdout and stderr"
        res = pxul.command.run(['echo', 'hello'], capture='both')
        self.assertEqual(res.out.strip(), 'hello')
        self.assertEqual(res.err.strip(), '')

    def test_capture_silent(self):
        "Should make stdout and stderr invisible"
        res = pxul.command.run(['echo', 'hello'], capture='silent')
        self.assertIsNone(res.out)
        self.assertIsNone(res.err)

    def test_raises_false_ok(self):
        "A valid command should run fine"
        res = pxul.command.run(['echo', 'hello'], capture='both', raises=False)
        self.assertEqual(res.out.strip(), 'hello')
        self.assertEqual(res.err.strip(), '')
        self.assertEqual(res.ret, 0)

    def test_raises_false_bad_command(self):
        "A failing command should return non-zero exit code"
        res = pxul.command.run(['touch', '/unallowed'],
                               capture='both', raises=False)
        self.assertEqual(res.out.strip(), '')
        self.assertTrue(res.err.startswith('touch: cannot touch'))
        self.assertNotEqual(res.ret, 0)


class Command_Test(TestCase):
    def test_init_check(self):
        "Should throw if command is malformed"
        c = 'ls'
        with self.assertRaises(pxul.command.ArgumentsError):
            pxul.command.Builder(c)

    def test_init_list1(self):
        "Should create a Command from a one-element list"
        c = ['ls']
        cmd = pxul.command.Builder(c)
        self.assertListEqual(cmd.cmd, c)

    def test_init_listN(self):
        "Should create a Command of an n-element list"
        c = ['echo'] + [str(i) for i in xrange(10)]
        cmd = pxul.command.Builder(c)
        self.assertListEqual(cmd.cmd, c)

    def test_call_no_args(self):
        "Call with no arguments"
        echo = pxul.command.Builder(['echo'], capture='both')
        out, err, ret = echo()
        self.assertEqual(out.strip(), '')
        self.assertEqual(err.strip(), '')
        self.assertEqual(ret, 0)

    def test_call_with_args(self):
        "Call with arguments"
        echo = pxul.command.Builder(['echo'], capture='both')
        out, err, ret = echo('hello', 'world')
        self.assertEqual(out.strip(), 'hello world')

    def test_object_immutable(self):
        "__call__ should not modify the state of the object"
        echo = pxul.command.Builder(['echo'], capture='silent')
        original = copy.deepcopy(echo.__dict__)
        echo('hello', 'world')
        self.assertDictEqual(original, echo.__dict__)
