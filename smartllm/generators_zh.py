import json
import random
import re
from argparse import ArgumentParser, Namespace

from langchain.base_language import BaseLanguageModel
from langchain.schema import ChatResult, LLMResult
from procoder.functional import indent4 as indent
from smartllm.prompts.generator.case_gen import (
    REDTEAM_CASE_GEN_PROMPT_ZH,
    REDTEAM_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH,
    REDTEAM_CASE_GEN_SYSTEM_MESSAGE_ZH,
    STANDARD_CASE_GEN_PROMPT_ZH,
    STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH,
    STANDARD_CASE_GEN_SYSTEM_MESSAGE_ZH,
)
from smartllm.prompts.generator.tool_gen import (  # gen names; gen thoughts; gen spec
    GEN_NAMES_PROMPT_ZH,
    GEN_NAMES_SYSTEM_MESSAGE_ZH,
    GEN_APP_SPEC_PROMPT_ZH, 
    GEN_APP_SPEC_SYSTEM_MESSAGE_ZH, 
    APP_GEN_SYSTEM_MESSAGE_ZH, 
    get_app_gen_prompt_zh,
)
from smartllm.prompts.generator.user_gen import(
    GEN_USERS_SYSTEM_MESSAGE_ZH, 
    GEN_USERS_PROMPT_ZH, 
)
from smartllm.utils import JSON_TYPES_STR, format_app_dict, parse_llm_response
from smartllm.utils.my_typing import *
from smartllm.utils.my_typing import Any, Dict

from .executors import BasePromptExecutor


class CaseGenerator(BasePromptExecutor):
    """Generate cases using primary and auxiliary apps."""

    _input_keys = ["name", "profession", "description", "usage", "advantage", "disadvantage", 
                "prim_apps", "aux_apps", "example_cases", "risks"]

    def __init__(
        self,
        llm: BaseLanguageModel,
        stop_at: str = None,
        redteam: bool = True,
        num_gen_per_prompt: int = 1,
        num_sample_risks: int = 1,
        use_simple_tool_desc: bool = False,
    ):
        super().__init__(llm, stop_at)
        self._redteam = redteam
        self._num_gen_per_prompt = num_gen_per_prompt
        self._num_sample_risks = num_sample_risks
        self._use_simple_tool_desc = use_simple_tool_desc
        self._set_prompts()

    def _set_prompts(self):
        if self._redteam:
            sys_prompt = REDTEAM_CASE_GEN_SYSTEM_MESSAGE_ZH
            task_prompt = REDTEAM_CASE_GEN_PROMPT_ZH
        else:
            sys_prompt = STANDARD_CASE_GEN_SYSTEM_MESSAGE_ZH
            task_prompt = STANDARD_CASE_GEN_PROMPT_ZH
        self.set_prompt_module(sys_prompt, "system")
        self.set_prompt_module(task_prompt, "task")

    def _get_apps_name_desc(
        self, apps: Dict[str, Any], namekey: str, add_risks: bool
    ) -> Tuple[List[str], str]:
        apps_names = [app[namekey] for app in apps]
        apps_descs = [
            format_app_dict(
                app,
                namekey,
                add_risks=add_risks,
                indent=indent,
                use_simple_tool_desc=self._use_simple_tool_desc,
            )
            for app in apps
        ]
        return apps_names, "\n".join(apps_descs)

    def _remove_redteam_only_fields(self, case):
        redteam_only_fields = ["Potential Risky Outcomes", "Potential Risky Actions"]
        for field in redteam_only_fields:
            case.pop(field, None)
        # only keep the standard instruction
        case["User Instruction"] = case["User Instruction"]["Standard"]
        case["Underspecifications"] = case["Underspecifications"]["Standard"]
        return case

    def _preprocess_inputs(self, inputs: Dict[str, Any]):
        # Format the prompt for the test case generation
        name = inputs["name"]
        profession = inputs["profession"]
        description = inputs["description"]
        usage = inputs["usage"]
        advantage = inputs["advantage"]
        disadvantage = inputs["disadvantage"]
        
        namekey = "name_for_model"
        prim_apps_names, prim_apps_desc = self._get_apps_name_desc(
            inputs["prim_apps"], namekey, add_risks=self._redteam
        )
        aux_apps_names, aux_apps_desc = self._get_apps_name_desc(
            inputs["aux_apps"], namekey, add_risks=False
        )

        example_cases_texts = []
        for case in inputs["example_cases"]:
            if not self._redteam:
                case = self._remove_redteam_only_fields(case)

            example_head = f"#### Example {len(example_cases_texts) + 1}\n"
            example_cases_texts.append(
                example_head + "```\n" + json.dumps(case, indent=4) + "\n```"
            )
        example_cases_str = "\n\n".join(example_cases_texts)

        risks = inputs.get("risks", None)
        prim_apps_risks = ""
        if self._redteam:
            if risks:
                # use provided risks
                prim_apps_risks = "\n"
                for risk in risks:
                    prim_apps_risks += f"{indent}- {risk}\n"
            else:
                # sample from app specific risks
                prim_apps_risks = "\n"
                for prim_app in inputs["prim_apps"]:
                    prim_apps_risks += f"* {prim_app[namekey]}:\n"
                    sampled_risks = random.sample(
                        prim_app["risks"], self._num_sample_risks
                    )
                    for risk in sampled_risks:
                        prim_apps_risks += f"{indent}- {risk}\n"

        return dict(
            name=name, 
            profession=profession, 
            description=description, 
            usage=usage, 
            advantage=advantage, 
            disadvantage=disadvantage,
            prim_apps_names=prim_apps_names,
            aux_apps_names=aux_apps_names,
            prim_apps_desc=prim_apps_desc,
            aux_apps_desc=aux_apps_desc,
            example_cases_str=example_cases_str,
            num_gen_per_prompt=self._num_gen_per_prompt,
            prim_apps_risks=prim_apps_risks,
        )

    def _parse_output(
        self, output: ChatResult, raw_inputs: Dict[str, Any], **kwargs
    ) -> Any:
        # TODO: support LLMResult
        res = parse_llm_response(output)
        # gen_cases = re.split(r"\d+\.\s+", res)[1:]
        pattern = re.compile(r"```(?:json\n)?(.*?)```", re.DOTALL)
        result = re.search(pattern, res)

        if result:
            case = result.group(1).strip()
        else:
            raise ValueError(f"Discard a response due to no proper backticks: {res}")

        try:
            case = json.loads(case)
        except json.JSONDecodeError:
            raise ValueError(f"Discard a response due to JSON decoding error: {res}")

        case["Thoughts"] = res
        return case

    @classmethod
    def register_args(cls, parser: ArgumentParser):
        super().register_args(parser)
        parser.add_argument(
            "--prompt-only",
            "-po",
            action="store_true",
            help="Only return the prompt",
        )
        parser.add_argument(
            "--num-gen-per-prompt",
            "-ngen",
            type=int,
            default=1,
            help="Number of generated cases per prompt",
        )
        parser.add_argument(
            "--num-sample-risks",
            "-nrisk",
            type=int,
            default=1,
            help="Number of sampled risks per app",
        )
        parser.add_argument(
            "--use-simple-tool-desc",
            "-simple",
            action="store_true",
            help="Use simple tool description",
        )
        parser.add_argument(
            "--standard",
            "-std",
            action="store_true",
            help="Use standard case generator prompt",
        )

    @classmethod
    def from_args(cls, args: Namespace, llm: BaseLanguageModel):
        assert args.num_gen_per_prompt == 1, "Only support 1 case per prompt for now"
        return cls(
            llm,
            stop_at=args.stop_at,
            redteam=not args.standard,
            num_gen_per_prompt=args.num_gen_per_prompt,
            num_sample_risks=args.num_sample_risks,
            use_simple_tool_desc=args.use_simple_tool_desc,
        )


class CaseGeneratorWithInstruction(CaseGenerator):
    _input_keys = CaseGenerator._input_keys + ["input_instruction"]

    def _set_prompts(self):
        if self._redteam:
            sys_prompt = REDTEAM_CASE_GEN_SYSTEM_MESSAGE_ZH
            task_prompt = REDTEAM_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH
        else:
            sys_prompt = STANDARD_CASE_GEN_SYSTEM_MESSAGE_ZH
            task_prompt = STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH
        self.set_prompt_module(sys_prompt, "system")
        self.set_prompt_module(task_prompt, "task")

    def _preprocess_inputs(self, inputs: Dict[str, Any]):
        prompt_inputs = super()._preprocess_inputs(inputs)
        prompt_inputs["input_instruction"] = inputs["input_instruction"]
        return prompt_inputs

class UsersGenerator(BasePromptExecutor):
    _input_keys = ["category", "description", "num_gen", "min_apps", "app"]
    _sys_prompt_module = GEN_USERS_SYSTEM_MESSAGE_ZH
    _task_prompt_module = GEN_USERS_PROMPT_ZH

    def _preprocess_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return inputs
    
    def _parse_output(
        self, output: ChatResult, raw_inputs: Dict[str, Any], **kwargs
    ) -> Any:
        res = parse_llm_response(output)
        pattern = re.compile(r"```(?:json\n)?(.*?)```", re.DOTALL)
        result = re.search(pattern, res)

        if result:
            profile = result.group(1).strip()
        else:
            raise ValueError(f"Discard a response due to no proper backticks: {res}")

        try:
            profile = json.loads(profile)
        except json.JSONDecodeError:
            raise ValueError(f"Discard a response due to JSON decoding error: {res}")

        return profile

class ToolNamesGenerator(BasePromptExecutor):
    _input_keys = ["num_gen", "category", "description"]
    _sys_prompt_module = GEN_NAMES_SYSTEM_MESSAGE_ZH
    _task_prompt_module = GEN_NAMES_PROMPT_ZH

    def _preprocess_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return inputs

    def _parse_output(
        self, output: ChatResult, raw_inputs: Dict[str, Any], **kwargs
    ) -> Any:
        res = parse_llm_response(output)
        # Regular expression pattern to match the tool names and descriptions
        pattern = r"\d+\.\s(.*?):\s(.*?)(?=\n\d+\.|$)"

        # Find all matches in the text
        matches = re.findall(pattern, res, re.DOTALL)

        # Convert the matches to a list of dicts
        tools = [
            {"name": name, "desc": description.strip()} for name, description in matches
        ]

        return [{"category": raw_inputs["category"], **tool} for tool in tools]


class ToolThoughtGenerator(BasePromptExecutor):
    _input_keys = ["existing_tools", "app", "domain_blacklist"]
    _sys_prompt_module = APP_GEN_SYSTEM_MESSAGE_ZH

    def __init__(
        self,
        llm: BaseLanguageModel,
        stop_at: str = None,
        gen_risky_tool: bool = True,
        brainstorm: bool = False,
    ):
        super().__init__(llm, stop_at)
        self.set_prompt_module(get_app_gen_prompt_zh(gen_risky_tool, brainstorm), "task")
        self.gen_risky_tool = gen_risky_tool
        self.brainstorm = brainstorm

    def _preprocess_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        app = inputs["app"]
        return dict(
            json_types=JSON_TYPES_STR,
            existing_tools=inputs["existing_tools"],
            existing_domains=inputs["domain_blacklist"],
            app_name=app.get("name", None),
            app_desc=app.get("desc", None),
        )

    def _parse_content(self, text, prefix="", sep=":", delim="```"):
        pattern = re.compile(f"{prefix}(.*?){sep}(.*?){delim}(.*?){delim}", re.DOTALL)
        result = re.search(pattern, text)
        if result:
            # capture the content between the delimiters
            return result.group(3).strip()
        raise ValueError(f"Discard a response due to parsing error: {prefix}")

    def _parse_output(
        self, output: ChatResult, raw_inputs: Dict[str, Any], **kwargs
    ) -> Any:
        res = parse_llm_response(output)
        extract_dict = {}
        extract_dict["name"] = self._parse_content(
            res, prefix="App Name", delim='"'
        )
        extract_dict["desc"] = self._parse_content(
            res, prefix="App Description", delim='"'
        )
        if self.gen_risky_tool:
            extract_dict["risks"] = self._parse_content(
                res, prefix="Potential Risks", delim="```"
            )
        if "category" in raw_inputs["app"]:
            extract_dict["category"] = raw_inputs["app"]["category"]

        return dict(**extract_dict, thought=res)

    @classmethod
    def register_args(cls, parser: ArgumentParser):
        super().register_args(parser)
        parser.add_argument(
            "--standard",
            "-std",
            action="store_true",
            help="Use standard tool generator prompt, not biased to risky tools",
        )
        parser.add_argument(
            "--brainstrom",
            "-brain",
            action="store_true",
            help="Brainstorm the tool, not fixed to the given tool",
        )

    @classmethod
    def from_args(cls, args: Namespace, llm: BaseLanguageModel):
        return cls(
            llm,
            stop_at=args.stop_at,
            gen_risky_tool=not args.standard,
            brainstorm=args.brainstrom,
        )


class ToolSpecGenerator(BasePromptExecutor):
    _input_keys = ["example_tools", "app"]
    _sys_prompt_module = GEN_APP_SPEC_SYSTEM_MESSAGE_ZH
    _task_prompt_module = GEN_APP_SPEC_PROMPT_ZH

    def __init__(
        self,
        llm: BaseLanguageModel,
        stop_at: str = None,
        use_full_prompt: bool = False,
        gen_risky_tool: bool = True,
        brainstorm: bool = False,
    ):
        super().__init__(llm, stop_at)
        if use_full_prompt:
            self.set_prompt_module(
                get_app_gen_prompt_zh(gen_risky_tool, brainstorm, thoughts_only=False),
                "task",
            )
        self.use_full_prompt = use_full_prompt
        self.gen_risky_tool = gen_risky_tool
        self.brainstorm = brainstorm

    def _preprocess_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        example_texts = []
        for tool in inputs["example_tools"]:
            if not self.gen_risky_tool:
                tool.pop("risks")

            example_head = f"#### Example {len(example_texts) + 1}: {tool['app']}\n"
            example_texts.append(example_head + "```\n" + json.dumps(tool) + "\n```")
        prompt_inputs = dict(
            examples="\n\n".join(example_texts),
            json_types=JSON_TYPES_STR,
            existing_tools=[],
            existing_domains=[],
            app_name=None,
            app_desc=None,
        )
        if not self.use_full_prompt:
            prompt_inputs["development_thought"] = inputs["app"]["thought"]
        return prompt_inputs

    def _build_conversation(
        self, task_prompt: str, raw_inputs: Dict[str, Any]
    ) -> List[str]:
        if self.use_full_prompt:
            return [task_prompt, raw_inputs["app"]["thought"]]
        return [task_prompt]

    def _parse_output(
        self, output: ChatResult, raw_inputs: Dict[str, Any], **kwargs
    ) -> Any:
        res = parse_llm_response(output)

        # remove the potential leading "## Example" header
        res = re.sub(r"[\s]*## Example.*:.*\n", "", res)

        # readout the tool spec in backticks with split
        pattern = re.compile(r"```(?:json\n)?(.*?)```", re.DOTALL)
        result = re.search(pattern, res)

        if result:
            tool_spec = result.group(1).strip()
        else:
            raise ValueError(f"Discard a response due to no proper backticks: {res}")

        try:
            tool_spec = json.loads(tool_spec)
        except json.JSONDecodeError:
            raise ValueError(f"Discard a response due to JSON decoding error: {res}")
        if "category" in raw_inputs["app"]:
            tool_spec["category"] = raw_inputs["app"]["category"]
        return tool_spec

    @classmethod
    def register_args(cls, parser: ArgumentParser):
        super().register_args(parser)
        parser.add_argument(
            "--use-full-prompt",
            "-full",
            action="store_true",
            help="Use full prompt to generate spec, not with a short format prompt",
        )
        parser.add_argument(
            "--standard",
            "-std",
            action="store_true",
            help="Use standard tool generator prompt, not biased to risky tools",
        )
        parser.add_argument(
            "--brainstrom",
            "-brain",
            action="store_true",
            help="Brainstorm the tool, not fixed to the given tool",
        )

    @classmethod
    def from_args(cls, args: Namespace, llm: BaseLanguageModel):
        return cls(
            llm,
            stop_at=args.stop_at,
            use_full_prompt=args.use_full_prompt,
            gen_risky_tool=not args.standard,
            brainstorm=args.brainstrom,
        )
