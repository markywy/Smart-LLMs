"""
Emulate the agent's app-use trajectories.

Usage: python scripts/emulate_zh.py -inp <input_cases_file> -atp <agent_type> -stp <simulator_type> -ctp <case_type>
"""

import argparse
import os
import random

import anthropic
import openai.error
from dotenv import load_dotenv
from smartllm.agent_executor_builder_zh import build_agent_executor
from smartllm.agents import AGENT_TYPES, SIMULATORS_ZH
from smartllm.dataloader import DataLoader
from smartllm.executors import FuncExecutorWithRetry
from smartllm.apps import *
from smartllm.utils import (
    case_to_input_dict,
    filter_keys,
    get_app_names,
    llm_register_args,
    load_openai_llm_with_args,
    replace_agent_action_with_list,
    read_file, 
    CASE_ATTRS_TO_KEYS_MAPPING
)
from smartllm.utils.my_typing import *
from copy import deepcopy

load_dotenv()
ROLES = ["agent", "simulator"]

parser = argparse.ArgumentParser()
for role in ROLES:
    llm_register_args(parser, prefix=role)
DataLoader.register_args(parser)
FuncExecutorWithRetry.register_args(
    parser, default_num_retries=5, default_batch_size=5, default_timeout=1800
)
parser.add_argument("--dump-dir", "-du", type=str, default="./dumps/trajectories")
parser.add_argument(
    "--output-file-suffix",
    "-outsuf",
    type=str,
    default="",
)
parser.add_argument(
    "--agent-type",
    "-atp",
    type=str,
    default="naive",
    choices=AGENT_TYPES,
)
parser.add_argument(
    "--simulator-type",
    "-stp",
    type=str,
    default="std_thought",
    choices=list(SIMULATORS_ZH.keys()),
)
parser.add_argument("--max-iterations", "-mi", type=int, default=15)
parser.add_argument("--verbose", "-v", action="store_true")
parser.add_argument("--random-seed", "-seed", type=int, default=42)

args = parser.parse_args()
random.seed(args.random_seed)

def main():
    llms = {role: load_openai_llm_with_args(args, prefix=role) for role in ROLES}
    cases = DataLoader.from_args(args, return_mode="with_idx", item_name="case")
    runner = FuncExecutorWithRetry.from_args(args)
    os.makedirs(args.dump_dir, exist_ok=True)
    output_path = os.path.join(
        args.dump_dir,
        (
            f"traj_sim_{args.simulator_type}_agent_{args.agent_model_name}"
            f"_{args.agent_type}{args.output_file_suffix}_zh.jsonl"
        ),
    )

    def generate_trajectory(case_with_idx):
        case_idx, case = case_with_idx["idx"], case_with_idx["item"]
        for k in CASE_ATTRS_TO_KEYS_MAPPING:
            if (k == "name"): continue
            if k not in case.keys():
                failed_item = case_with_idx
                outputs = {f"error: \"{k}\" is not in case {case_idx}"}
                return failed_item, outputs
        user=case["User"]
        agent_executer = build_agent_executor(
            user,
            get_app_names(case), 
            llms["agent"],
            llms["simulator"],
            agent_type=args.agent_type,
            simulator_type=args.simulator_type,
            verbose=args.verbose,
            max_iterations=args.max_iterations,
        )
        case_= deepcopy(case)
        for k in case_.keys():
            if k not in CASE_ATTRS_TO_KEYS_MAPPING:
                case.pop(k)
        inputs = filter_keys(case_to_input_dict(case, case_type="std"), agent_executer.input_keys)
        try:
            outputs = agent_executer(inputs)
            failed_item = None
        except (openai.error.InvalidRequestError, anthropic.BadRequestError) as e:
            print(f"{case_idx}: {str(e)}")
            outputs = {"error": str(e)}
            failed_item = case_with_idx
        outputs = replace_agent_action_with_list(outputs)  # ad-hoc fix
        outputs["case"] = case
        outputs["case_idx"] = case_idx
        return failed_item, outputs

    runner.run(generate_trajectory, output_path, cases)
    print(
        "You may want to use scripts to convert the result jsonl file "
        f"{output_path} to json for easier reading."
    )


if __name__ == "__main__":
    main()
