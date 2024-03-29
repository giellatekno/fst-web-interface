# thank you,
# https://stackoverflow.com/questions/3365740/how-to-import-all-submodules

import importlib as __importlib
import pkgutil as __pkgutil


def __import_submodules(package, recursive=True):
    """ Import all submodules of a module, recursively, including subpackages

    :param package: package (name or actual module)
    :type package: str | module
    :rtype: dict[str, types.ModuleType]
    """
    if isinstance(package, str):
        package = __importlib.import_module(package)
    results = {}
    for loader, name, is_pkg in __pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        results[full_name] = __importlib.import_module(full_name)
        if recursive and is_pkg:
            results.update(__import_submodules(full_name))

    return results


__import_submodules(__name__)
