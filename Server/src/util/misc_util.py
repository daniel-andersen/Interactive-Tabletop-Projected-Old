import imp


def module_exists(module_name):
    try:
        imp.find_module(module_name)
        return True
    except ImportError:
        return False
