"""
Run external commands

AUTHOR:
 - Badi' Abdul-Wahid

CHANGES:
 - 2015-06-12:
     - return Result from `call` (issue #26)
     - add `run` (issue #27)
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

import collections
import pipes
import subprocess
import types
import logging
logger = logging.getLogger()


PIPE = subprocess.PIPE
DEVNULL = open('/dev/null', 'w')


class ArgumentsError(Exception):
    "Indicates that parameters to a subprocess were malformed"
    pass


def check_cmd(cmd):
    """Raises ArgumentsError if malformed cmd.

    A command is malformed if it is a bare string. This is done to
    prevent injection of arbitrary commands by untrusted input.  For
    instance:

    >>> check_cmd('echo hello unsafe; rm -rf /')

    is dangerous and thus considered and error. The safer alternative
    is

    >>> check_cmd(['echo', 'hello', 'safe;', 'rm', '-rf', '/'])

    While a bit more verbose, enforcing this constraint for safety is
    the better trade-off.

    :param cmd: the command to check
    :raises: :class:`ArgumentsError` on failure.

    """
    if isinstance(cmd, types.StringType):
        raise ArgumentsError('Got bare string {}'.format(cmd))


class CalledProcessError(Exception):
    """Like :class:`subprocess.CalledProcessError` but with attributes for
    stderr and stdout
    """

    def __init__(self, cmd, retcode, stdout=None, stderr=None):
        self._cmd = cmd
        self._retcode = retcode
        self._stdout = stdout
        self._stderr = stderr

    @property
    def cmd(self):
        "The command used"
        return self._cmd

    @property
    def retcode(self):
        "The return value of the child process"
        return self._retcode

    @property
    def stdout(self):
        "The stdout captured from the child process"
        return self._stdout

    @property
    def stderr(self):
        "The stderr captured from the child process"
        return self._stderr


Result = collections.namedtuple('Result', ['out', 'err', 'ret'])


def call(cmd, stdin=None, stdout=None, stderr=None, buffer=-1, input=None):
    """Call an external command.

    :param cmd: the command to run
    :type cmd: :class:`list` or *iterable* of strings
    :param stdin: where to read stdin from
    :param stdout: where to write stdout to
    :param stderr: where to write stderr to
    :param buffer: the buffer size when communicating with the subprocess
    :param input: initial input to pass to stdin
    :returns: the stdout, stderr, and returncode as a namedtuple
    :rtype: :class:`Result`
    :raises: :class:`ArgumentsError`
             if the arguments are malformed (see :func:`check_cmd`)
    :raises: :class:`CalledProcessError` of the subprocess fails
    """
    logger.debug('Got command {}'.format(cmd))
    check_cmd(cmd)
    pretty = ' '.join(map(pipes.quote, cmd))
    logger.debug('Calling: {}'.format(pretty))
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
        raise CalledProcessError(pretty, proc.returncode,
                                 stdout=out,
                                 stderr=err)
    result = Result(out=out, err=err, ret=proc.returncode)
    return result


def run(cmd, capture=None, raises=True, buffer=-1, input=None):
    """Wrapper over :func:`call` with a simpler interface

    **Capture Options**


    - `stdout`: capture the standard output
    - `stderr`: capture the standard error
    - `both`: capture both stdout and stderr
    - `silent`: hide all output of the child process

    :param list of str cmd: the command to call (as in :func:`call`)
    :param str capture: capture options
    :param bool raises: raise an exception on non-zero return of child
    :param int buffer: buffer size (as in :class:`subprocess.Popen`)
    :param str input: input value (as in :class:`subprocess.Popen.communicate`)
    :returns: the result
    :rtype: :class:`Result`
    """
    kws = _capture_keywords(capture)

    try:
        return call(cmd, buffer=buffer, input=input, **kws)
    except CalledProcessError, e:
        if raises:
            raise
        else:
            return Result(out=e.stdout, err=e.stderr, ret=e.retcode)


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

    if capture == 'silent':
        kws['stdout'] = DEVNULL
        kws['stderr'] = DEVNULL

    return kws


class Builder(object):
    """Utility for building commands which can be called with more
    specific arguments later.

    Instances of :class:`Builder` are :func:`callable`. This is the
    intended usage when invoking a :class:`Builder` to call the
    subprocess.

    >>> echo = Builder(['echo', 'hello', capture='stdout')
    >>> print echo()[0].strip()
    hello
    >>> print echo('world')[0].strip()
    hello world
    >>> print echo('universe')[0].strip()
    hello universe
    """

    def __init__(self, cmd, capture=None):
        check_cmd(cmd)
        self.cmd = cmd
        self.capture = capture

    def add_args(self, args):
        check_cmd(args)
        self.cmd.extend(args)

    def __call__(self, *args, **call_kws):
        check_cmd(args)
        cmd = list(self.cmd) + list(args)

        kws = _capture_keywords(self.capture)
        call_kws.update(kws)
        return call(cmd, **call_kws)
