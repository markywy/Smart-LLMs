from .real_tools import *
from .register import get_app_dict, apps_factory
from .tool_interface import BaseApp, FunctionApp
# Prompt the user for input
simulate_lan = input("Enter language code (zh for Chinese, en for English): ").strip().lower()

try:
    if simulate_lan == 'zh':
        print('程序将在中文环境下运行')
        from .virtual_tools_zh import *
    elif simulate_lan == 'en':
        print('Code will be launched with English environment')
        from .virtual_tools import *
    else:
        print('error')
        raise ValueError("Invalid value for simulate_lan")
except ValueError as e:
    print(e)

def get_apps_by_names(names: List[str]) -> List[FunctionApp]:
    apps = []
    for name in names:
        app = apps_factory(name)
        if app:
            apps.append(app())
        else:
            print(f"Warning: app {name} not found")
    return apps


def get_tool_class_by_name(apps: List[FunctionApp], name: str) -> BaseTool:
    for app in apps:
        try:
            return app[name]
        except ValueError:
            pass
    raise ValueError(f"Tool {name} does not exist in these apps")
