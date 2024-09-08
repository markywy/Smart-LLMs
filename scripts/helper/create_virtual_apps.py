"""
Create virtual apps from json files.

# Usage example:
python scripts/create_virtual_apps.py --in-json-path <json file path> --out-py-path <output python file path>
"""

import argparse
import json
import os

from smartllm.utils import read_file

PY_HEADER = """
\"\"\"Virtual apps created from json files.\"\"\"
from smartllm.apps.app_interface import (
    ArgException,
    ArgParameter,
    ArgReturn,
    FunctionApp,
    FunctionApp,
    VirtualFunctionApp,
)
from smartllm.utils.my_typing import *

from .register import register_app
"""

SEPERATOR = """
#################### {app_name} ####################
"""

APP_CLASS_TEMPLATE = """
@register_app()
class {app_name}(FunctionApp):
    name_for_human = "{app_name_for_human}"
    description_for_human = "{app_description_for_human}"
    name_for_model = "{app_name_for_model}"
    description_for_model = "{app_description_for_model}"
    app_classes = {app_class_names}
"""

APP_CLASS_TEMPLATE = """
class {app_cls_name}(VirtualFunctionApp):
    name = "{app_cls_name}"
    summary = "{app_summary}"
    parameters: List[ArgParameter] = {parameters}
    returns: List[ArgReturn] = {returns}
    exceptions: List[ArgException] = {exceptions}
"""

args = argparse.ArgumentParser()
args.add_argument(
    "--app-spec-dir",
    "-d",
    type=str,
    default="./assets",
)
args.add_argument(
    "--app-spec-files",
    "-i",
    type=str,
    nargs="+",
    default=["all_apps.json"],
    help="Path to input json file containing app specifications.",
)
args.add_argument(
    "--out-py-path",
    "-o",
    type=str,
    default="./smartllm/apps/virtual_apps.py",
    help="Path to output python file containing app definitions.",
)
args = args.parse_args()


def main():
    app_specs = []
    # load app specifications from json file
    for filename in args.app_spec_files:
        filepath = os.path.join(args.app_spec_dir, filename)
        app_specs.extend(read_file(filepath))

    # the output file
    out_py = open(args.out_py_path, "w", encoding='utf-8')
    out_py.write(PY_HEADER)

    # create virtual apps
    for appspec in app_specs:
        app_name = appspec["app"]
        app_name_for_human = appspec["name_for_human"]
        app_name_for_model = appspec["name_for_model"]
        app_description_for_human = appspec["description_for_human"]
        app_description_for_model = appspec["description_for_model"]

        out_py.write(SEPERATOR.format(app_name=app_name))

        app_class_names = []
        for app in appspec["api"]:
            app_name = app["name"]
            app_cls_name = app_name_for_model + app_name
            app_class_names.append(app_cls_name)
            app_summary = app["summary"]
            app_parameters = app.get("parameters", [])
            app_returns = app.get("returns", [])
            app_exceptions = app.get("exceptions", [])

            out_py.write(
                APP_CLASS_TEMPLATE.format(
                    app_cls_name=app_cls_name,
                    app_summary=app_summary,
                    parameters=app_parameters,
                    returns=app_returns,
                    exceptions=app_exceptions,
                )
            )

        out_py.write(
            APP_CLASS_TEMPLATE.format(
                app_name=app_name,
                app_name_for_human=app_name_for_human,
                app_name_for_model=app_name_for_model,
                app_description_for_human=app_description_for_human,
                app_description_for_model=app_description_for_model,
                app_class_names="[{}]".format(", ".join(app_class_names)),
            )
        )

    out_py.close()
    # reformat the output file with black
    os.system("python -m black {}".format(args.out_py_path))


if __name__ == "__main__":
    main()
