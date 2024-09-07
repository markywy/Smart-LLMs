from .app_interface import BaseTool

__APPS_DICT__ = {}


def get_app_dict():
    return __APPS_DICT__


def apps_factory(name):
    return __APPS_DICT__.get(name, None)


def register_app(overwrite=None):
    def register_function_fn(cls):
        name = overwrite
        if name is None:
            name = cls.__name__
        if name in __APPS_DICT__:
            raise ValueError(f"Name {name} already registered!")
        if not issubclass(cls, BaseTool):
            raise ValueError(f"Class {cls} is not a subclass of {BaseTool}")
        __APPS_DICT__[name] = cls
        # print(f"App registered: [{name}]")
        return cls

    return register_function_fn
