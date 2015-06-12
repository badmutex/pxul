import pxul.os
import os
import os.path
import tempfile
import shutil
import uuid

from unittest import TestCase


class tmpdir_Test(TestCase):
    def test_directory_changed(self):
        "Entering the context should temporarily switch working directories"

        starting_cwd = os.getcwd()
        with pxul.os.tmpdir():
            new_cwd = os.getcwd()
            self.assertNotEqual(starting_cwd, new_cwd)

    def test_cleanup(self):
        "Exiting the context should remove the temporary directory"

        starting_cwd = os.getcwd()
        with pxul.os.tmpdir():
            new_cwd = os.getcwd()
            self.assertTrue(os.path.exists(new_cwd))
        final_cwd = os.getcwd()
        self.assertEqual(starting_cwd, final_cwd)
        self.assertFalse(os.path.exists(new_cwd))

    def test_context_as_keyword(self):
        "Entering should return the new path when using `with ctx as name`"

        with pxul.os.tmpdir() as tmpdir:
            cwd = os.getcwd()
            self.assertIsNotNone(tmpdir)
            self.assertEqual(tmpdir, cwd)


class in_dir_Test(TestCase):
    def test_directory_changed(self):
        "Entering the context should temporarily change directories"
        newdir = os.getenv('HOME')
        starting_cwd = os.getcwd()
        with pxul.os.in_dir(newdir):
            new_cwd = os.getcwd()
            self.assertNotEqual(starting_cwd, new_cwd)
            self.assertEqual(newdir, new_cwd)

    def test_cleanup(self):
        "Exiting the context should not remove the target directory"

        tmpdir = tempfile.mkdtemp()
        try:
            with pxul.os.in_dir(tmpdir):
                self.assertTrue(os.path.exists(tmpdir))
            self.assertTrue(os.path.exists(tmpdir))
        finally:
            os.rmdir(tmpdir)


class env_Test(TestCase):
    def new_env(self):
        name = 'SET_ENV_TEST_{}'.format(uuid.uuid4().hex)
        value = '{}'.format(uuid.uuid4().hex)
        return name, value

    def test_env_set(self):
        "Entering the context with keywords should update the environment"
        k0, v0 = self.new_env()
        self.assertIsNone(os.getenv(k0))

        k1, v1 = self.new_env()
        self.assertIsNone(os.getenv(k1))

        with pxul.os.env(**{k0: v0, k1: v1}):
            self.assertEqual(v0, os.getenv(k0))
            self.assertEqual(v1, os.getenv(k1))

    def test_env_noctx(self):
        "Manually activating/deactivating should work"
        env = pxul.os.env(SPAM='eggs')

        with self.assertRaises(KeyError):
            spam = os.environ['SPAM']

        env.activate()
        spam = os.environ['SPAM']
        self.assertEqual(spam, 'eggs')

        env.deactivate()
        with self.assertRaises(KeyError):
            spam = os.environ['SPAM']

    def test_cleanup(self):
        "Exiting the context should clear the environment"

        k, v = self.new_env()
        with pxul.os.env(**{k: v}):
            pass
        self.assertIsNone(os.getenv(k))


class remove_children_Test(TestCase):
    def test_cleanup(self):
        tmpdir = tempfile.mkdtemp()
        hello = os.path.join(tmpdir, 'hello.txt')
        try:
            with open(hello, 'w') as fd:
                fd.write('world\n')

            # should not be empty
            with self.assertRaises(OSError):
                os.rmdir(tmpdir)

            pxul.os.remove_children(tmpdir)

            # show now be empty
            os.rmdir(tmpdir)

        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir)


class ensure_dir_Test(TestCase):
    def test_absent(self):
        "ensure_dir should create a directory if not present"
        tmpname = 'tmp{}'.format(uuid.uuid4().hex)
        tmpdir = os.path.join(tempfile.gettempdir(), tmpname)

        try:
            self.assertFalse(os.path.exists(tmpdir))
            pxul.os.ensure_dir(tmpdir)
            self.assertTrue(os.path.exists(tmpdir))
        finally:
            if os.path.exists(tmpdir):
                os.rmdir(tmpdir)

    def test_present(self):
        "ensure_dir should not modify a directory that is already present"

        with pxul.os.tmpdir():
            cwd = os.getcwd()
            self.assertTrue(os.path.exists(cwd))

            stat_before = os.stat(cwd)
            pxul.os.ensure_dir(cwd)
            stat_after = os.stat(cwd)

            self.assertTrue(os.path.exists(cwd))
            self.assertEqual(stat_before, stat_after)


class fullpath_Test(TestCase):
    def test_expand_user(self):
        "Should expand ~"
        home = os.getenv('HOME')
        expanded = pxul.os.fullpath('~')
        self.assertEqual(home, expanded)

    def test_expand_vars(self):
        "Should expand variables"
        home = os.getenv('HOME')
        expanded = pxul.os.fullpath('$HOME')
        self.assertEqual(home, expanded)

    def test_abspath(self):
        "Should find the absolute path"
        name = uuid.uuid4().hex
        cwd = os.getcwd()
        real = os.path.join(cwd, name)
        expanded = pxul.os.fullpath(name)
        self.assertEqual(real, expanded)


class ensure_file_Test(TestCase):
    "`ensure_file` should be idempotent"

    def test_absent(self):
        "Should create an empty file if it does not exist"

        with pxul.os.tmpdir():
            name = 'hello.txt'

            self.assertFalse(os.path.exists(name))
            pxul.os.ensure_file(name)
            self.assertTrue(os.path.exists(name))

    def test_present(self):
        "Should not create a file if it already exists"
        with pxul.os.tmpdir():
            name = 'hello.txt'
            open(name, 'w').close()
            stat_before = os.stat(name)
            pxul.os.ensure_file(name)
            stat_after = os.stat(name)
            self.assertEqual(stat_before, stat_after)


class find_in_path_Test(TestCase):
    def test_success(self):
        "Should return the path to an executable"
        # sh is present on most systems
        path = pxul.os.find_in_path('sh')
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))

    def test_failure(self):
        "Should return None if absent"
        name = uuid.uuid4().hex
        path = pxul.os.find_in_path(name)
        self.assertIsNone(path)
