from tqdm import tqdm
import argparse
import os
import os.path as osp

from dotenv import load_dotenv
from smartllm.dataloader import DataLoader
from smartllm.executors import BaseFuncExecutor
from smartllm.generators_zh import UsersGenerator
from smartllm.utils import llm_register_args, load_openai_llm_with_args, read_file, write_json
from smartllm.utils.my_typing import *

load_dotenv()
parser = argparse.ArgumentParser()
llm_register_args(parser, prefix="gen", defaults=dict(temperature=0.6))
UsersGenerator.register_args(parser)
DataLoader.register_args(
    parser, default_input_path="assets/for_generation/user_taxonomy_zh.json"
)
BaseFuncExecutor.register_args(parser)
parser.add_argument("--apps-path", "-ap", type=str, default="./assets/all_apps_zh.json")
parser.add_argument("--dump-dir", "-du", type=str, default="./dumps/users")
parser.add_argument(
    "--output-file-name", "-out", type=str, default="gen_users_zh.jsonl"
)
parser.add_argument("--num-gen-per-cat", "-ng", type=int, default=15)
parser.add_argument("--min-apps", "-mt", type=int, default=2)
args = parser.parse_args()

os.makedirs(args.dump_dir, exist_ok=True)
output_file = osp.join(args.dump_dir, args.output_file_name)
llm = load_openai_llm_with_args(args, prefix="gen")
generator = UsersGenerator.from_args(args, llm)
taxonomy = DataLoader.from_args(args)
runner = BaseFuncExecutor.from_args(args, multiple_results=True)    

apps = read_file(args.app_path)
print(f"Loaded {len(apps)} apps")
name2app = {app["app"]: app for app in apps}
all_app_names = list(name2app.keys())   
app = [app["app"] for app in apps]

taxonomies = read_file(args.input_path)
print(f"Loaded {len(taxonomies)} taxonomies")

results = []
for taxonomy in tqdm(taxonomies):
    inputs = dict(
        category = taxonomy["category"],
        description = taxonomy["description"],
        num_gen = args.num_gen_per_cat,
        min_apps = args.min_apps, 
        app = app, 
    )
    result = generator(inputs)
    # print(result)
    results.append(result)

os.makedirs(args.dump_dir, exist_ok=True)
write_json(results, output_file)