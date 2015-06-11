"""
Run external commands

AUTHOR:
 - Badi' Abdul-Wahid

CHANGES:
 - 2015-06-11:
     - reimplement everything (issue #3)
 - 2014-07-25:
     - propagate CTRL-C to subprocess
     - support specification of flag prefix
     - Process learned to accept Popen keyword parameters
 - 2014-04-04:
     - Add Process
     - Add Command
     - Add OptCommand
"""
from __future__ import absolute_import

import pipes
import subprocess
import types
import logging
logger = logging.getLogger()


PIPE = subprocess.PIPE


class ArgumentsError(Exception):
    "Indicates that parameters to a subprocess were malformed"
    pass


def check_cmd(cmd):
    "Raises ArgumentsError if malformed cmd"
    if isinstance(cmd, types.StringType):
        raise ArgumentsError('Got bare string {}'.format(cmd))


class CalledProcessError(Exception):
    "subprocess.CalledProcessError but with attributes for stderr and stdout"
    def __init__(self, cmd, retcode, stdout=None, stderr=None):
        self.cmd = cmd
        self.retcode = retcode
        self.stdout = stdout
        self.stderr = stderr


def call(cmd, stdin=None, stdout=None, stderr=None, buffer=-1, input=None):
    logger.debug('Got command {}'.format(cmd))
    check_cmd(cmd)
    logger.debug('Calling: {}'.format(' '.join(map(pipes.quote, cmd))))
    proc = subprocess.Popen(cmd, stdin=stdin, stdout=stdout, stderr=stderr,
                            bufsize=buffer)

    try:
        out, err = proc.communicate(input=input)
    except KeyboardInterrupt:
        logger.debug('Caught SIGINT, terminating subprocess')
        proc.terminate()
        proc.kill()
        raise

    logger.debug('Subprocess finished with {}'.format(proc.returncode))
    if proc.returncode is not 0:
        raise CalledProcessError(proc.returncode, cmd, stdout=out, stderr=err)

    return out, err, proc.returncode


def silent(*args, **kws):
    with open('/dev/null', 'w') as devnull:
        kws['stdout'] = devnull
        kws['stderr'] = devnull
        return call(*args, **kws)


def capture_keywords(capture):
    kws = {}
    if capture == 'stdout' or capture == 'both':
        kws['stdout'] = PIPE

    if capture == 'stderr' or capture == 'both':
        kws['stderr'] = PIPE

    return kws


class Command(object):
    def __init__(self, cmd, silent=False, capture=None):
        check_cmd(cmd)
        self.cmd = cmd
        self.silent = silent
        self.capture = capture

        if silent and capture:
            raise ValueError(
                "Both 'silent' and 'capture' cannot both be enabled")

    def add_args(self, args):
        check_cmd(args)
        self.cmd.extend(args)

    def __call__(self, *args, **call_kws):
        check_cmd(args)
        cmd = list(self.cmd) + list(args)

        if self.silent:
            return silent(cmd, **call_kws)
        else:
            kws = capture_keywords(self.capture)
            call_kws.update(kws)
            return call(cmd, **call_kws)
