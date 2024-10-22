import json
import random
import re
from ast import literal_eval

from langchain.agents.tools import InvalidTool as LangChainInvalidApp
from langchain.callbacks.stdout import StdOutCallbackHandler
from langchain.tools import BaseTool

from .my_typing import *

PRIMITIVE_TYPES = {
    "integer": int,
    "number": float,
    "string": str,
    "boolean": bool,
    "array": List,
    "object": Dict,
    "null": None,
}


def insert_indent(s: str, indent: str = "\t", insert_first=True) -> str:
    prefix = indent if insert_first else ""
    return prefix + s.rstrip("\n ").replace("\n", "\n" + indent) + "\n"


def create_str(
    data: Dict[str, str], include_desc: bool = True, indent: str = "\t"
) -> str:
    name = data["name"]
    prefix = f"{indent}- " if include_desc else ""
    desc = f": {data['description']}" if include_desc else ""
    type = ""
    if "type" in data:
        type = data["type"]
        if not data.get("required", True):
            type += ", optional"
        type = f" ({type})"
    return f"{prefix}{name}{type}{desc}"


class ArgParameter(TypedDict):
    """The input parameter for a app"""

    name: str
    type: str
    description: str
    required: bool


class ArgReturn(TypedDict):
    """The return value for a app"""

    name: str
    type: str
    description: str


class ArgException(TypedDict):
    """The exception for a app"""

    name: str
    description: str


class DummyAppWithMessage(BaseTool):
    """App that is run when invalid situation is encountered by agent."""

    name = "dummy_app_with_message"
    description = "Called when app is not actually run."

    def _get_message(self, msg: str) -> str:
        return msg

    def _run(self, msg: str) -> str:
        return self._get_message(msg)

    async def _arun(self, msg: str) -> str:
        return self._get_message(msg)


class InvalidApp(DummyAppWithMessage):
    """App that is run when invalid app name is encountered by agent."""

    name = "invalid_app"
    description = "Called when app name is invalid."
    available_apps: List[str]

    def _get_message(self, app_name: str) -> str:
        availabel_app_string = ", ".join(self.available_apps)
        err_msg = (
            f"{app_name} is not a valid app, try another one. "
            f"You should use available apps in [{availabel_app_string}] only. "
            "If you cannot (or do not need to) use any existing apps to improve your response, "
            "conclude by stating Final Answer directly."
        )

        return f'{{"error": "InvalidRequestException: {err_msg}"}}'


def special_fix_for_json_obj(s: str, pos: int) -> str:
    """Fix the string to make it a valid JSON object."""
    if pos >= len(s):
        return None
    if s[pos] == "\\":  # fix for {"xxx\_yyy": "zzz"}
        broken = s[pos : pos + 2]
        return s.replace(broken, broken[1])
    elif s[pos : pos + 4] == "True":
        return s.replace("True", "true")
    elif s[pos : pos + 5] == "False":
        return s.replace("False", "false")
    return None


def get_first_json_object_str(s: str, enable_check=True, *args, **kwargs) -> str:
    """Get the first JSON object from a string"""
    # print("[DEBUG] raw action string:", s)
    # allow ```json {JSON object} ``` format
    regex = r"```(?:json)?\s*(\{.*?\})\s*```"
    match = re.search(regex, s, flags=re.DOTALL)
    if match:
        s = match.group(1)

    # Assume the JSON object is at the beginning of the string
    s = s.lstrip()
    ret = s

    while True:
        try:
            _ = json.loads(s, *args, **kwargs)
            break
        except json.JSONDecodeError as e:
            fix_res = special_fix_for_json_obj(s, e.pos)  # special fixes
            if fix_res is not None:
                ret = s = fix_res
            else:
                s = s[: e.pos].rstrip()  # take the first part
                break
    try:
        _ = json.loads(s, *args, **kwargs)  # check if the first part is valid JSON
        ret = s  # if pass the check, return the string after processing
    except Exception as e:
        if enable_check:
            raise e
    return ret


def load_dict(app_input: str) -> Dict[str, Any]:
    """Load a dictionary from a string."""
    # TODO: improve this, this seems to be the most robust way for now
    try:
        params = json.loads(app_input, strict=False)
        # set strict=False to allow single quote, comments, escape characters, etc
        return params
    except Exception as e:
        msg = str(e)
        if msg.startswith("Invalid \\escape"):
            raise ValueError(
                # f"Invalid syntax for \\escape, you may need to use \\\\ instead"
                f"Invalid syntax for \\', you may need to use \\\\' instead"
            )
        raise ValueError(
            f"Invalid format: {e}. Please format it as a JSON object with necessary fields matching the app's argument specifications. Do not include backsticks to wrap the JSON object."
        )


def match_type(value: Any, expected_type: type) -> bool:
    if isinstance(value, expected_type):
        return True
    # allow int to be float
    return isinstance(value, int) and expected_type == float


def check_type(name: str, value: Any, expected_type: type):
    if not match_type(value, expected_type):
        raise ValueError(
            f"Invalid type for {name}: {type(value).__name__}, "
            f"expected {expected_type.__name__}."
        )


def validate_inputs(parameters: List[ArgParameter], inputs: Dict[str, Any]):
    """Validate the inputs for a app."""
    remains = set(inputs.keys())
    for param in parameters:
        name = param["name"]
        if name in remains:
            remains.remove(name)
        if name in inputs:
            expected_type = PRIMITIVE_TYPES[param["type"]]
            check_type(name, inputs[name], expected_type)
        elif param.get("required", False):
            raise ValueError(f"Missing required parameter: {name}.")
    if remains:
        raise ValueError(f"Unexpected parameters: {remains}.")


def validate_outputs(returns: List[ArgReturn], outputs: Dict[str, Any]):
    """Validate the outputs for a app."""
    if not isinstance(outputs, dict):
        raise ValueError(
            f"Invalid type for outputs: {type(outputs).__name__}, expected dict."
        )
    if list(outputs.keys()) == ["error"]:  # raised exception
        return  # no need to validate
    remains = set(outputs.keys())
    for ret in returns:
        name = ret["name"]
        if name in remains:
            remains.remove(name)
        if name not in outputs:
            raise ValueError(f"Missing return: {name}.")
        expected_type = PRIMITIVE_TYPES[ret["type"]]
        check_type(name, outputs[name], expected_type)
    if remains:
        raise ValueError(f"Unexpected returns: {list(remains)}.")


def run_with_input_validation(
    run_func: Callable,
    inputs: Dict[str, str],
    app: BaseTool,
    raw_inputs: str,
    **kwargs,
):
    """Run a app with inputs, where the format of raw inputs is validated."""
    try:
        params = load_dict(raw_inputs)
        validate_inputs(app.parameters, params)
    except Exception as e:
        return DummyAppWithMessage().run(
            f'{{"error": "InvalidRequestException: {e}"}}', **kwargs
        )

    return run_func(inputs, **kwargs)


def find_app_spec(name: str, apps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find a app specification by name."""
    for app in apps:
        if app["app"] == name:
            return app
    raise ValueError(f"App not found: {name}.")


def format_app_dict(
    app: Dict[str, Any],
    namekey: str,
    add_risks: bool = True,
    indent: str = "\t",
    use_simple_app_desc: bool = False,
):
    """Format a app specified as a dictionary into a string."""
    app_name = app[namekey]
    desc = f"<{app_name}> app with following app APIs:\n"
    for app in app["api"]:
        if use_simple_app_desc:
            summary = app["summary"].rstrip("\n ")
            desc += f"{indent}* {app['name']}: {summary}\n"
        else:
            summary = app["summary"].rstrip("\n ")
            desc += f"{indent}* {app['name']}"
            params = []
            for p in app["parameters"]:
                params.append(f"{p['name']}")
            desc += f"({', '.join(params)})"
            returns = []
            for r in app["returns"]:
                returns.append(f"{r['name']}")
            desc += f" -> {', '.join(returns)}"
            desc += f" : {summary}\n"

    if add_risks and "risks" in app:
        desc += "Potential Risky Outcomes:\n"
        risks = list(app["risks"])
        random.shuffle(risks)
        for risk in risks:
            desc += f"{indent}* {risk}\n"
    return desc
