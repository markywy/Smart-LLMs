from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.generator.app_gen.shared_zh import *
from smartllm.utils import get_num_tokens, make_colorful

STD_APP_GEN_GENERAL_TASK_DESC_ZH = NamedBlock(
    "Task Description",
    APP_GEN_GENERAL_TASK_DESC_ZH,
)

ORIG_APP_GEN_PROMPT_ZH = (
    Collection(
        STD_APP_GEN_GENERAL_TASK_DESC_ZH,
        APP_GEN_REQUIREMENTS_ZH,
        APP_GEN_BLACKLIST_ZH,
        APP_FORMAT_ZH,
        APP_GEN_TASK_INSTRUCTION_ZH,
    )
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing)
    # .enable_name()
)


def remove_risky_req(prompt):
    brainstorm_app_step = find_submodule(prompt, "brainstorm_app_step")
    prompt = removed_submodules(
        prompt,
        [
            "risky_requirement",
            "app_risks",
            "potential_risks",
            "brainstorm_app_risks",
            "assess_risks",
            "no_unauthorized_access_risk",
        ],
    )

    replace_func = lambda x: x.replace(", {risky_requirement}", "")
    brainstorm_app_step = replace_prompt(brainstorm_app_step, replace_func)
    prompt = replaced_submodule(
        prompt, "brainstorm_app_step", brainstorm_app_step
    )

    return prompt


STD_APP_GEN_PROMPT_ZH = remove_risky_req(ORIG_APP_GEN_PROMPT_ZH)


STD_APP_GEN_FIXED_PROMPT_ZH = apply_gen_fixed_app_prompt(STD_APP_GEN_PROMPT_ZH)
STD_APP_GEN_BRAINSTORMED_PROMPT_ZH = apply_gen_brainstormed_app_prompt(
    STD_APP_GEN_PROMPT_ZH
)

STD_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH = remove_spec_format_instruction(
    STD_APP_GEN_FIXED_PROMPT_ZH
)
STD_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH = remove_spec_format_instruction(
    STD_APP_GEN_BRAINSTORMED_PROMPT_ZH
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
        gen_prompt = STD_APP_GEN_FIXED_PROMPT_ZH
        gen_thought_prompt = STD_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH
    else:
        gen_prompt = STD_APP_GEN_BRAINSTORMED_PROMPT_ZH
        gen_thought_prompt = STD_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH

    print("\n\nSTD App Gen Prompt:")
    print_prompt(gen_prompt)

    print("\n\nSTD App Gen Thoughts Prompt:")
    print_prompt(gen_thought_prompt)
