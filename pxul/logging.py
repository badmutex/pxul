"""
Provide a simple logger to `stdout` or `stderr`

>>> import pxul
>>> pxul.logging.debug()
>>> from pxul.logging import logger
>>> logger.debug('fooey')
>>> logger.info('hello world')
>>> logger.critical('Launching missiles')


AUTHORS:
 - Badi' Abdul-Wahid

CHANGES:
 - Add `Logger`, `lvl_name`, and `set_<level>` functions

"""
from __future__ import absolute_import
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
import sys

INFO1 = INFO-1
INFO2 = INFO-2

class Logger(object):
    """
    A simple logger that writes to a stream interface, eg `sys.stdout` or `sys.stderr`
    """
    def __init__(self, lvl=DEBUG, stream=sys.stdout):
        self._lvl    = lvl
        self._stream = stream

    def set_level(self, lvl):
        self._lvl = lvl

    def log(self, lvl, *args, **kws):
        if lvl < self._lvl: return
        strs = len(args) * ['%s']
        fmt  = '%-9s ' % lvl_name(lvl) + ' '.join(strs)
        fmt  += '\n'
        args = map(str, args)
        args = map(lambda s: s.replace('\n', '\n' + 10*' '), args)
        self._stream.write(fmt % tuple(args))

    def notset   (self, *args, **kws): return self.log(INFO2   , *args, **kws)
    def debug    (self, *args, **kws): return self.log(DEBUG   , *args, **kws)
    def info2    (self, *args, **kws): return self.log(INFO2   , *args, **kws)
    def info1    (self, *args, **kws): return self.log(INFO1   , *args, **kws)
    def info     (self, *args, **kws): return self.log(INFO    , *args, **kws)
    def warning  (self, *args, **kws): return self.log(WARNING , *args, **kws)
    def error    (self, *args, **kws): return self.log(ERROR   , *args, **kws)
    def critical (self, *args, **kws): return self.log(CRITICAL, *args, **kws)


def lvl_name(lvl):
    if   lvl <= NOTSET   : return 'NOTSET'
    elif lvl <= DEBUG    : return 'DEBUG'
    elif lvl <= INFO2    : return 'INTO2'
    elif lvl <= INFO1    : return 'INFO1'
    elif lvl <= INFO     : return 'INFO'
    elif lvl <= WARNING  : return 'WARNING'
    elif lvl <= ERROR    : return 'ERROR'
    elif lvl <= CRITICAL : return 'CRITICAL'

logger = Logger(INFO)

# set loggin level
def set_debug()    : logger.set_level(DEBUG)
def set_info2()    : logger.set_level(INFO2)
def set_info1()    : logger.set_level(INFO1)
def set_info()     : logger.set_level(INFO)
def set_warning()  : logger.set_level(WARNING)
def set_error()    : logger.set_level(ERROR)
def set_critical() : logger.set_level(CRITICAL)
