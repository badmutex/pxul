
try:
    from .version import version, time_version, git_version, full_version
except ImportError:
    version = 'UNKNOWN'
