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
    """Raises ArgumentsError if malformed cmd.

    A command is malformed if it is a bare string. This is done to
    prevent injection of arbitrary commands by untrusted input.  For
    instance:

    >>> check_cmd('echo hello unsafe; rm -rf /')

    is dangerous. The safer alternative is

    >>> check_cmd(['echo', 'hello', 'safe;', 'rm', '-rf', '/'])

    While a bit more verbose, enforcing this constraint for safety is
    the better trade-off.

    :param cmd: the command to check
    :raises: :class:`ArgumentsError` on failure.

    """
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
    """Call an external command.

    :param cmd: the command to run
    :type cmd: :class:`list` or *iterable* of strings
    :param stdin: where to read stdin from
    :param stdout: where to write stdout to
    :param stderr: where to write stderr to
    :param buffer: the buffer size when communicating with the subprocess
    :param input: initial input to pass to stdin
    :returns: the stdout, stderr, and returncode
    :rtype: 3-:class:`tuple`
    """
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
    """Wraps :func:`call` but redirects *stdout* and *stderr* to ``/dev/null``

    :args: arguments to :func:`call`
    :kwargs: keyword arguments to :func:`call`
    :returns: the return code of the subprocess
    :rtype: :class:`int`
    """
    with open('/dev/null', 'w') as devnull:
        kws['stdout'] = devnull
        kws['stderr'] = devnull
        _, _, ret = call(*args, **kws)
        return ret


def _capture_keywords(capture):
    """Generate the keywords to capture the output of a subprocess

    :param capture: one of {stdout | stderr | both}
    :returns: the keyword arguments
    :rtype: :class:`dict`
    """
    kws = {}
    if capture == 'stdout' or capture == 'both':
        kws['stdout'] = PIPE

    if capture == 'stderr' or capture == 'both':
        kws['stderr'] = PIPE

    return kws


class Builder(object):
    """Utility for building commands which can be called with more
    specific arguments later.

    Instances of :class:`Builder` are :func:`callable`. This is the
    intended usage when invoking a :class:`Builder` to call the
    subprocess.

    >>> echo = Builder(['echo', 'hello', capture='stdout')
    >>> out, _, _ = echo()
    >>> out == '\\n'
    True
    >>> out, _, _ = echo('world')
    >>> print out
    world
    >>> out, _, _ = echo('universe')
    >>> print out
    universe

    """
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
            kws = _capture_keywords(self.capture)
            call_kws.update(kws)
            return call(cmd, **call_kws)
