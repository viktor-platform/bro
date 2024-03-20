import bro.__version__ as _version
from bro.api import *
from bro.helper_functions import *
from bro.objects import *

# has to be set explicitly as attribute to be accessible from pyproject.toml # TODO: pyproject.tom can also get version directly from git tag, sounds like a better idea
__version__ = _version.__version__
