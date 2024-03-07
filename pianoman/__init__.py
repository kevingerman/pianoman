from .config import Config
import os

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def get_config(conf={}, fname=None, envprefix=Config._prefix):
    env = {k.replace(envprefix, ''): os.getenv(k) for k in
           filter(lambda x: x.startswith(envprefix), os.environ)}
    fname = fname if fname and os.path.exists(fname) else conf.get('configfile',
                                                                   env.get('configfile'))
    return Config(fname).override(env).override(conf, skipdefaults=True)
