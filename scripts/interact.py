import argparse
from smartllm.utils import (
    read_file, 
)

simulate_lan = input("Enter language code (zh for Chinese, en for English): ").strip().lower()

try:
    if simulate_lan == 'zh':
        print('程序将在中文环境下运行')
    elif simulate_lan == 'en':
        print('Code will be launched with English environment')
    else:
        print('error')
        raise ValueError("Invalid value for simulate_lan")
except ValueError as e:
    print(e)

parser = argparse.ArgumentParser()
parser.add_argument("--input-path", "-inp", type=str, default="dumps/trajectories/traj_sim_std_thought_agent_gpt-4o-mini_naive_eval_agent_safe.jsonl")
args = parser.parse_args()

results = read_file(args.input_path)

for result in results:
    if ("0" in result["Overall Quantitative Score"]):
        if (simulate_lan == "zh"):
            print("用户输入：", result["input"])
            print("已拦截风险。Agent 反馈：\n", result["Evaluator Thought"])
            print("请修改你的指令以确保 Agent 的安全性：")
            rewrite = input()
            print("已反馈，正在重新生成...")
        else:
            print("User Input:", result["input"])
            print("Risks blocked. Agent Response:\n", result["Evaluator Thought"])
            print("Please rewrite your instruction to ensure the safety of the agent:")
            rewrite = input()
            print("Instruction feedbacked. Regenerating...")
    