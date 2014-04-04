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

import os
import subprocess
import shlex


class Process(object):
    def __init__(self, cmd):
        self.cmd = cmd

    def __call__(self):
        logger.info1('EXECUTING: %s' % self.cmd)
        proc = subprocess.Popen(self.cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode is not 0:
            raise subprocess.CalledProcessError(proc.returncode,
                                                self.cmd, err + out)
        logger.debug('OUTPUT:\n', out + err)
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

    def __call__(self, **kws):
        # prepare the parameters
        parms = list()
        for k, v in kws.iteritems():
            if len(k) == 1:
                flag = '-' + k
            else:
                flag = '--' + k
            if v is None: continue
            elif type(v) is bool and v:
                arg = flag
            else:
                arg = '%s %s' % (flag, v)
            self.o(arg)

        # run
        return super(OptCommand, self).__call__()

