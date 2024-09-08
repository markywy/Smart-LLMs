"""Generate apps from spec from thoughts"""
# NOTE: some convertion from thoughts to spec might exceed context length.
# You need to reduce the context length, or use claude or gpt-3.5-16k instead.

import argparse
import os.path as osp
import random

from dotenv import load_dotenv
from smartllm.dataloader import DataLoader
from smartllm.executors import BaseFuncExecutor
from smartllm.generators import AppSpecGenerator
from smartllm.utils import (
    llm_register_args,
    load_openai_llm_with_args,
    print_intermediate_result_and_stop,
    read_file,
)
from smartllm.utils.my_typing import *

load_dotenv()
parser = argparse.ArgumentParser()

llm_register_args(parser, prefix="gen")
AppSpecGenerator.register_args(parser)
DataLoader.register_args(parser)
BaseFuncExecutor.register_args(parser)

parser.add_argument(
    "--format-example-file",
    "-fe",
    type=str,
    default="./assets/for_generation/format_example_app.json",
)
parser.add_argument("--random-seed", "-seed", type=int, default=42)
args = parser.parse_args()
random.seed(args.random_seed)

llm = load_openai_llm_with_args(args, prefix="gen")
generator = AppSpecGenerator.from_args(args, llm)
runner = BaseFuncExecutor.from_args(args)


def main():
    app_thoughts = DataLoader.from_args(args, item_name="app thought")
    format_example = read_file(args.format_example_file)
    output_file = f"{osp.splitext(app_thoughts._input_path)[0]}_spec.jsonl"

    if generator._stop_at in ["preprocess", "prompt"]:
        result = generator(
            dict(example_apps=[format_example], app=app_thoughts[0])
        )
        print_intermediate_result_and_stop(result, generator._stop_at)

    def transform_thought(thought):
        inputs = dict(example_apps=[format_example], app=thought)
        try:
            return None, generator(inputs)
        except Exception as e:
            print(f"Error encountered: {e}")
            return thought, None

    _, remaining_dataset, _ = runner.run(transform_thought, output_file, app_thoughts)
    print(f"{len(remaining_dataset)} apps failed to be generated.")


if __name__ == "__main__":
    main()
