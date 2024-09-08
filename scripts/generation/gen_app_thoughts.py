"""Generate apps from seed apps"""

import argparse
import datetime
import os
import os.path as osp
import random

from dotenv import load_dotenv
from smartllm.dataloader import DataLoader
from smartllm.executors import GenFuncExecutor
from smartllm.generators import AppThoughtGenerator
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
llm_register_args(parser, prefix="gen", defaults=dict(temperature=0.5))
DataLoader.register_args(parser, default_input_path="")
AppThoughtGenerator.register_args(parser)
GenFuncExecutor.register_args(parser)

parser.add_argument(
    "--apps-paths",
    "-ap",
    type=str,
    nargs="+",
    default=["./assets/all_apps.json"],
)
parser.add_argument("--dump-dir", "-du", type=str, default="./dumps/apps")
parser.add_argument("--gen-filename", "-gen", type=str, default="gen_app_thoughts")
parser.add_argument(
    "--output-mode", "-om", choices=["overwrite", "append", "new"], default="new"
)
parser.add_argument("--random-seed", "-seed", type=int, default=42)
args = parser.parse_args()

random.seed(args.random_seed)
os.makedirs(args.dump_dir, exist_ok=True)
llm = load_openai_llm_with_args(args, prefix="gen")
generator = AppThoughtGenerator.from_args(args, llm)
runner = GenFuncExecutor.from_args(args)


def main():
    apps = []
    for f in args.apps_paths:
        apps.extend(read_file(f))
    print(f"Loaded {len(apps)} apps")
    existing_app_names = set([t["app"] for t in apps])

    os.makedirs(args.dump_dir, exist_ok=True)
    base_name = args.gen_filename + ("_risky" if generator.gen_risky_app else "_std")
    if args.output_mode == "new":
        base_name += f"_{NOW}"
    output_file = osp.join(args.dump_dir, f"{base_name}.jsonl")
    if os.path.exists(output_file) and args.output_mode == "overwrite":
        os.remove(output_file)

    try:
        app_names = list(DataLoader.from_args(args, item_name="app name"))
    except Exception as e:
        print(e)
        app_names = None

    if generator.brainstorm:
        if runner._target_num is None:
            raise ValueError("Please specify --target-num when brainstorming new apps")
        dataset = None
    else:
        if app_names is None:
            raise ValueError(
                "Please specify app names with --input-path when using fixed app names for generation"
            )
        dataset = [i for i in range(len(app_names))]

    def build_inputs(index: int):
        if generator.brainstorm:
            app = {}
        else:
            app = app_names[index]
        inputs = dict(
            existing_apps=existing_app_names,
            app=app,
            domain_blacklist=None,
        )
        return inputs

    if generator._stop_at in ["preprocess", "prompt"]:
        result = generator(build_inputs(0))
        print_intermediate_result_and_stop(result, generator._stop_at)

    def generate_app_thoughts(index: int):
        inputs = build_inputs(index)

        try:
            return None, generator(inputs)
        except Exception as e:
            print(e)
            return index, None

    runner.run(generate_app_thoughts, output_file, dataset=dataset)


if __name__ == "__main__":
    main()
