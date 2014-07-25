"""
Run external commands

AUTHOR:
 - Badi' Abdul-Wahid

CHANGES:
 - 2014-04-04:
     - Add Process
     - Add Command
     - Add OptCommand
"""
from __future__ import absolute_import

from .logging import logger
from .StringIO import StringIO

import copy
import os
import subprocess
import shlex


class ProcessError(Exception):
    def __init__(self, retcode, cmd, out):
        msg = 'Command {} returned non-zero exit code {}\n{}'.format(cmd, retcode, out)
        super(ProcessError, self).__init__(msg)

class Process(object):
    def __init__(self, cmd, **kws):
        self.cmd = cmd
        self.popen_kws = kws

    def __call__(self):
        s = self.cmd if type(self.cmd) is str else ' '.join(self.cmd)
        logger.info1('EXECUTING: %s' % s)
        proc = subprocess.Popen(self.cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                **self.popen_kws)
        try:
            out, err = proc.communicate()
        except KeyboardInterrupt:
            proc.terminate()
            proc.kill()
            raise

        logger.debug('OUTPUT:\n', out + err)
        if proc.returncode is not 0:
            raise ProcessError(proc.returncode, self.cmd, err + out)

        return out, err


class Command(object):
    def __init__(self, path):
        self._cmd = [path]

    @property
    def name(self):
        """Name of the command to execute"""
        return self._cmd[0]

    def o(self, arg):
        """Add CLI option"""
        self._cmd.extend(shlex.split(arg))
        return self

    def __str__(self):
        return '<%s>' % ' '.join(map(repr, self._cmd))

    def __repr__(self):
        with StringIO() as sio:
            sio.write('Command(%r)' % self.name)
            for o in self._cmd[1:]:
                sio.writeln('.o(%r)' % repr(o))
            return sio.getvalue()

    def __call__(self):
        return Process(self._cmd)()


class OptCommand(Command):
    """
    A process that can take short-form command line parameters as keyword
    arguments. Since arguments passed to __call__ are processed in
    lexicographical order, this precludes using `OptCommand` for commands
    in which the order of parameters is important.

    Single-character keywords are prepend by a single dash '-' while longer ones
    have a double-dash '--' prepended.

    e.g.:
    To run: foo -a arga -b argb -c --foo --bar 42
    Write:  OptCommand('foo')(a='arga', b='argb', c=True, foo=True bar=32)

    Returns: (stdout, stderr)
    """

    def __init__(self, *args, **kws):
        long_pref = kws.pop('long_flag_prefix', '--')
        short_pref = kws.pop('short_flag_prefix', '-')
        super(OptCommand, self).__init__(*args, **kws)
        self._long_flag_prefix = long_pref
        self._short_flag_prefix = short_pref

    def __call__(self, **kws):
        # make a copy so that multiple calls don't keep updating the
        # parameter list
        tmp_cmd = copy.deepcopy(self._cmd)
        for k, v in kws.iteritems():
            if len(k) == 1:
                flag = self._short_flag_prefix + k
            else:
                flag = self._long_flag_prefix + k
            if v is None: continue
            elif type(v) is bool and v:
                arg = flag
            else:
                arg = '%s %s' % (flag, v)
            self.o(arg)

        # run
        result = super(OptCommand, self).__call__()
        self._cmd = tmp_cmd
        return result

