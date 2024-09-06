import json
import random
import re
from argparse import ArgumentParser, Namespace

from langchain.schema import ChatResult, LLMResult
from procoder.functional import removed_submodules
from procoder.prompt import Module as PromptModule
from smartllm.prompts.evaluator import (
    AGENT_HELP_EVALUATOR_PROMPT,
    AGENT_HELP_EVALUATOR_SYSTEM_INFO,
    AGENT_SAFE_EVALUATOR_PROMPT,
    AGENT_SAFE_EVALUATOR_SYSTEM_INFO,
)
from smartllm.prompts.globals import GENERAL_CRITIQUE_PROMPT, GENERAL_SUMMARIZE_PROMPT
from smartllm.apps import get_apps_by_names
from smartllm.utils import (
    METRICS_SHORT2LONG,
    case_to_input_dict,
    construct_trajec,
    get_app_names,
    get_used_tools_in_trajec,
    parse_llm_response,
)
from smartllm.utils.my_typing import *
from smartllm.utils.my_typing import Any, Dict, List

from .executors import BasePromptExecutorWithCritique


class BaseTrajEvaluator(BasePromptExecutorWithCritique):
    _short_name: str = None
    _input_keys: List[str] = ["trajectory"]
    _output_keys: List[str] = [
        "Evaluator Thought",
        "Overall Qualitative Label",
        "Overall Quantitative Score",
        "Evaluator Log Summary",
    ]
    _keys2metrics: Dict[str, str] = None
    _critique_prompt_module: PromptModule = GENERAL_CRITIQUE_PROMPT
    _summarize_prompt_module: PromptModule = GENERAL_SUMMARIZE_PROMPT
    _final_answer_in_traj: bool = True
    _app_desc_detail_level: str = "low"  # use simple app descriptions
    _used_tool_desc_detail_level: str = None

    def _preprocess_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        traj = inputs["trajectory"]
        if "error" in traj:
            raise ValueError(f"Error in eval trajec: {traj['error']}")

        apps = get_apps_by_names(get_app_names(traj["case"]))
        app_descs = {
            detail_level: "\n".join(
                [f"{app.create_description(detail_level)}" for app in apps]
            )
            for detail_level in ["low", "medium", "high"]
        }
        user = traj["case"]["User"]
        inputs = dict(
            tool_names=", ".join([tool.name for tool in apps]),
            app_descriptions=app_descs[self._app_desc_detail_level],
            name=user["Name"], 
            profession=user["Profession"], 
            description=user["Description"], 
            usage=user["Usage"], 
            advantage=["Advantages"], 
            disadvantage=["Disadvantages"], 
        )

        used_tool_level = self._used_tool_desc_detail_level
        if used_tool_level is not None:
            used_tool_names = get_used_tools_in_trajec(traj)
            used_tools = []
            for app in apps:
                for tool in app.tools:
                    if tool.name in used_tool_names:
                        used_tools.append(tool)
            used_tools_desc = "\n".join(
                [
                    f"* {tool.name}: {tool.create_description(used_tool_level)}"
                    for tool in used_tools
                ]
            )
            inputs["used_tools_descriptions"] = used_tools_desc

        return inputs

    def _fill_case_info(
        self,
        prompt_inputs: Dict[str, Any],
        case: Dict[str, Any],
        case_type: str = "legacy",
    ):
        inputs = case_to_input_dict(case, case_type)
        prompt_inputs.update(inputs)

    def _preprocess_prompts(
        self, prompts: List[PromptModule], prompt_inputs: Dict[str, Any]
    ) -> List[PromptModule]:
        return prompts

    def _postprocess_prompts(
        self, prompts: List[str], raw_inputs: Dict[str, Any]
    ) -> List[str]:
        traj = raw_inputs["trajectory"]
        traj_text = construct_trajec(
            traj,
            include_input=False,
            is_dumped_dict=True,
            include_agent_log=False,
            include_simulator_log=False,
            include_final_answer=self._final_answer_in_traj,
        )

        processed_prompts = []
        for prompt, name in zip(prompts, self._prompt_module_names):
            if name == "task":
                inputs = dict(evaluator_scratchpad=traj_text)
                self._fill_case_info(
                    inputs, traj["case"], traj.get("case_type", "std")
                )
                prompt = prompt.format(**inputs)
            processed_prompts.append(prompt)

        return processed_prompts

    def _parse_output(
        self, output: ChatResult, raw_inputs: Dict[str, Any], **kwargs
    ) -> Any:
        res = parse_llm_response(output)
        eval_res = {k: None for k in self._output_keys}
        eval_res["eval_scores"] = {}

        pattern = ""
        for k in self._output_keys:
            pattern += k + r":\s*(.*?)\s*"
        pattern += "$"
        matches = re.search(pattern, res, re.DOTALL)
        if matches is not None:
            for i, k in enumerate(self._output_keys):
                eval_res[k] = matches.group(i + 1)
                if self._keys2metrics is not None and k in self._keys2metrics:
                    eval_res["eval_scores"][self._keys2metrics[k]] = eval_res[k]

        return eval_res


class AgentRiskyAppCallEvaluator(BaseTrajEvaluator):
    _short_name = "agent_safe"
    _sys_prompt_module = AGENT_SAFE_EVALUATOR_SYSTEM_INFO
    _task_prompt_module = AGENT_SAFE_EVALUATOR_PROMPT
    _keys2metrics = {"Overall Quantitative Score": METRICS_SHORT2LONG[_short_name]}


class AgentHelpfulnessEvaluator(BaseTrajEvaluator):
    _short_name = "agent_help"
    _sys_prompt_module = AGENT_HELP_EVALUATOR_SYSTEM_INFO
    _task_prompt_module = AGENT_HELP_EVALUATOR_PROMPT
    _keys2metrics = {"Overall Quantitative Score": METRICS_SHORT2LONG[_short_name]}


EVALUATORS = [
    AgentRiskyAppCallEvaluator,
    AgentHelpfulnessEvaluator,
]
EVALUATORS = {e._short_name: e for e in EVALUATORS}
EVALUATORS2METRICS = {k: v._keys2metrics.values() for k, v in EVALUATORS.items()}
