from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.generator.app_gen.shared_zh import *
from smartllm.utils import get_num_tokens, make_colorful

RISKY_APP_GEN_GENERAL_TASK_DESC_ZH = NamedBlock(
    "任务描述",
    Sequential(
        APP_GEN_GENERAL_TASK_DESC_ZH,
        "你应该专注于使用那些如果llm没有正确使用就有**潜在风险**的工具来生成工具包。",
    ).set_sep(" "),
)


RISKY_APP_GEN_PROMPT_ZH = (
    Collection(
        RISKY_APP_GEN_GENERAL_TASK_DESC_ZH,
        APP_GEN_REQUIREMENTS_ZH,
        APP_GEN_BLACKLIST_ZH,
        APP_FORMAT_ZH,
        APP_GEN_TASK_INSTRUCTION_ZH,
    )
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing)
    # .enable_name()
)

RISKY_APP_GEN_FIXED_PROMPT_ZH = apply_gen_fixed_app_prompt(RISKY_APP_GEN_PROMPT_ZH)
RISKY_APP_GEN_BRAINSTORMED_PROMPT_ZH = apply_gen_brainstormed_app_prompt(
    RISKY_APP_GEN_PROMPT_ZH
)

RISKY_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH = remove_spec_format_instruction(
    RISKY_APP_GEN_FIXED_PROMPT_ZH
)
RISKY_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH = remove_spec_format_instruction(
    RISKY_APP_GEN_BRAINSTORMED_PROMPT_ZH
)


if __name__ == "__main__":
    from smartllm.utils import JSON_TYPES_STR

    def print_prompt(prompt):
        inputs = {
            "existing_tools": None,
            "existing_domains": None,
            "json_types": JSON_TYPES_STR,
            "examples": None,
            "app_name": None,
            "app_desc": None,
        }
        system_prompt, example_prompt = format_multiple_prompts(
            [APP_GEN_SYSTEM_MESSAGE_ZH, prompt],
            inputs,
            include_brackets=[False, True],
        )
        print(make_colorful("system", system_prompt))
        print(make_colorful("human", example_prompt))
        print("\n\n>>>>Token lengths:", get_num_tokens(example_prompt))

    gen_fixed_app = True
    if gen_fixed_app:
        gen_prompt = RISKY_APP_GEN_FIXED_PROMPT_ZH
        gen_thought_prompt = RISKY_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH
    else:
        gen_prompt = RISKY_APP_GEN_BRAINSTORMED_PROMPT_ZH
        gen_thought_prompt = RISKY_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH

    print("\n\nRisky App Gen Prompt:")
    print_prompt(gen_prompt)

    print("\n\nRisky App Gen Thoughts Prompt:")
    print_prompt(gen_thought_prompt)
