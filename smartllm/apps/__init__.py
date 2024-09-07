from .real_apps import *
from .register import get_app_dict, apps_factory
from .app_interface import BaseTool, FunctionApp
from .virtual_apps import *

def get_apps_by_names(names: List[str]) -> List[FunctionApp]:
    apps = []
    for name in names:
        app = apps_factory(name)
        if app:
            apps.append(app())
        else:
            print(f"Warning: app {name} not found")
    return apps


def get_app_class_by_name(apps: List[FunctionApp], name: str) -> BaseTool:
    for app in apps:
        try:
            return app[name]
        except ValueError:
            pass
    raise ValueError(f"App {name} does not exist in these apps")
