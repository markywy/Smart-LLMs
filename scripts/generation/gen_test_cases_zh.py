"""Generate redteam cases from seed cases"""

import argparse
import datetime
import os
import os.path as osp
import random

from tqdm import tqdm

import numpy as np
from dotenv import load_dotenv
from smartllm.executors import GenFuncExecutor
from smartllm.generators_zh import CaseGenerator
from smartllm.utils import (
    llm_register_args,
    load_openai_llm_with_args,
    print_intermediate_result_and_stop,
    read_file,
)
from smartllm.utils.my_typing import *

load_dotenv()
NOW = datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

parser = argparse.ArgumentParser()
llm_register_args(parser, prefix="gen", defaults=dict(temperature=1.0))
CaseGenerator.register_args(parser)
GenFuncExecutor.register_args(parser)
parser.add_argument("--dump-dir", "-du", type=str, default="./dumps/cases")
parser.add_argument("--gen-filename", "-gen", type=str, default="gen_cases")

parser.add_argument(
    "--apps-paths",
    "-tp",
    nargs="+",
    type=str,
    default=["./assets/all_apps_zh.json"],
)
parser.add_argument(
    "--risk-file-path",
    "-risk",
    type=str,
    default="./assets/for_generation/app_risks_zh.json",
)
parser.add_argument(
    "--users-file-path", 
    "-user", 
    type=str,
    default="./assets/all_users_zh.json"
)
parser.add_argument(
    "--format-examples-folder", "-fe", type=str, default="./assets/for_generation"
)
parser.add_argument(
    "--prim-apps",
    "-primt",
    type=str,
    nargs="+",
    default=None,
    help="subset apps to be sampled from for primary apps",
)
parser.add_argument("--num-prim-apps", "-npt", type=int, default=1)
parser.add_argument(
    "--aux-apps",
    "-auxt",
    type=str,
    nargs="+",
    default=None,
    help="subset apps to be sampled from for auxiliary apps",
)
parser.add_argument("--num-aux-apps", "-nat", type=int, default=3)
parser.add_argument("--use-aux-ratio", "-uar", type=float, default=0.5)
parser.add_argument("--num-example-cases", "-ne", type=int, default=1)
parser.add_argument(
    "--output-mode", "-om", choices=["overwrite", "append", "new"], default="new"
)
parser.add_argument("--random-seed", "-seed", type=int, default=None)
args = parser.parse_args()

FIXED_AUX_APPS = ["WindowsPowerShell"]  # apps that should always be included

if args.random_seed is not None:
    random.seed(args.random_seed)
    np.random.seed(args.random_seed)
llm = load_openai_llm_with_args(args, prefix="gen")
case_generator = CaseGenerator.from_args(args, llm)
runner = GenFuncExecutor.from_args(args)

apps = []
for f in args.apps_paths:
    apps.extend(read_file(f))
print(f"Loaded {len(apps)} apps")
app_risks = read_file(args.risk_file_path)

users = read_file(args.users_file_path)
print(f"Loaded {len(users)} users")

def get_app_names(full, subset=None):
    if subset is None:
        return full
    return [name for name in full if name in subset]

def main(idx: int):

    name2app = {app["app"]: app for app in apps}
    all_app_names = list(name2app.keys())
    prim_apps_names = get_app_names(all_app_names, args.prim_apps)
    aux_app_names = get_app_names(all_app_names, args.aux_apps)

    os.makedirs(args.dump_dir, exist_ok=True)
    base_name = args.gen_filename
    if args.output_mode == "new":
        base_name += f"_{NOW}"
    output_file = osp.join(args.dump_dir, f"{base_name}.jsonl")
    if os.path.exists(output_file) and args.output_mode == "overwrite":
        os.remove(output_file)

    zero_shot_format_example = read_file(
        os.path.join(args.format_examples_folder, "format_example_case_zero.json")
    )
    few_shot_format_examples = read_file(
        os.path.join(args.format_examples_folder, "format_example_cases.json")
    )

    def sample_inputs():
        user = users[idx]
        prims = random.sample(prim_apps_names, args.num_prim_apps)
        if ("WindowsPowerShell" not in prims): prims.append("WindowsPowerShell")

        remains = list(set(aux_app_names) - set(prims))
        auxs = []
        if args.use_aux_ratio <= 0.0:
            auxs = []
        elif random.random() < args.use_aux_ratio:
            auxs = random.sample(remains, args.num_aux_apps)

            for app_name in FIXED_AUX_APPS:
                if app_name not in prims and app_name not in auxs:
                    auxs.append(app_name)
        
        prim_apps = [name2app[name] for name in prims]
        aux_apps = [name2app[name] for name in auxs]
        risks = []
        for name in prims:
            risks.extend(app_risks.get(name, []))

        # choose example cases
        n_examples = args.num_example_cases
        if n_examples > 0:
            example_cases = random.sample(few_shot_format_examples, n_examples)
        else:
            example_cases = [zero_shot_format_example]

        inputs = dict(
            name=user["name"], 
            profession=user["profession"], 
            description=user["description"], 
            usage=user["usage"], 
            advantage=user["advantages"], 
            disadvantage=user["disadvantages"], 
            prim_apps=prim_apps,
            aux_apps=aux_apps,
            example_cases=example_cases,
            risks=risks,
        )
        return inputs

    if case_generator._stop_at in ["preprocess", "prompt"]:
        result = case_generator(sample_inputs())
        print_intermediate_result_and_stop(result, case_generator._stop_at)

    def generate_test_cases(index: int):
        inputs = sample_inputs()

        try:
            return None, case_generator(inputs)
        except Exception as e:
            print(e)
            return index, None

    runner.run(generate_test_cases, output_file)


if __name__ == "__main__":
    for i in tqdm(range(0, len(users)), total=len(users)):
        main(i)