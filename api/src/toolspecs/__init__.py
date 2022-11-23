#from pathlib import Path
#from importlib import import_module

from . import paradigm
from . import disambiguate

toolspecs = [paradigm, disambiguate]


# TODO
# import all files (modules) from this folder (package)
# dynamically without having to do the thing above

#thisdir = Path(__file__).parent
#glob = (f.name[:-3] for f in thisdir.glob("*.py"))
#names = (f for f in glob if f != "__init__")
#
#toolspecs = []
#for name in names:
#    print(name)
#    mod = import_module(".", name)
#    #toolspecs.append(import_module(".", name))
#
#[f for f in glob if f != "__init__"]
