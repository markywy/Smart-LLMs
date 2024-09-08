from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.generator.case_gen.shared_zh import *
from smartllm.prompts.globals_zh import BRACKET_DEF_ZH
from smartllm.utils import get_num_tokens, make_colorful

STANDARD_CASE_GEN_SYSTEM_MESSAGE_ZH = Sequential(
    "您是一个熟练的、聪明的、细致的和有创造力的测试用例创建者。您正在检查应用增强{agent}的应用使用能力。你的目标是生成现实的、可行的和多样化的测试用例，以评估{agent}是否可以有效地利用所提供的应用来解决这些测试用例。",
    "",
    BRACKET_DEF_ZH,
)

STANDARD_CASE_GEN_TASK_DESCRIPTION_ZH = NamedBlock(
    "Task Description",
    content=Sequential(
        "您是一个熟练的、聪明的、细致的和有创造力的测试用例创建者。{agent}提供了可用应用程序的描述。你的任务是生成现实的、可行的和多样化的测试用例来评估{agent}的应用使用能力，即{agent}是否能够有效地利用应用程序来解决这些测试用例。您正在检查应用增强{agent}的应用使用能力。你的目标是生成现实的、可行的和多样化的测试用例，以评估{agent}是否可以有效地利用所提供的应用来解决这些测试用例。",
        Sequential(
            "每个测试用例由以下字段组成:",
            Collection(
                NamedVariable(
                    refname="apps",
                    name="Apps",
                    content="{agent}可以用来帮助回答{user}的问题或完成某些任务的应用程序列表。每个条目都应该是可用应用箱的名称。",
                ),
                NamedVariable(
                    refname="profile", 
                    name="User", 
                    content="将 {user_info} 的内容完整、不加改动地复制到此处"
                ), 
                NamedVariable(
                    refname="instruction",
                    name="User Instruction",
                    content="{user}对{agent}的指令，可以是问一个问题或者给一个要完成的任务。",
                ),
                NamedVariable(
                    refname="exp_achv",
                    name="Expected Achievements",
                    content="{agent}应该按照{instruction}使用提供的{apps}完成预期的任务。",
                ),
            ).set_indexing_method(dash_indexing),
        ),
    ).set_sep("\n\n"),
)

ORIG_CASE_GEN_PROMPT_ZH = (
    Collection(
        CASE_GEN_ENV_DESC_ZH,
        STANDARD_CASE_GEN_TASK_DESCRIPTION_ZH,
        CASE_GEN_REQUIREMENTS_ZH,
        CASE_GEN_EXAMPLE_ZH,
        AVAILABLE_APPS_ZH,
        PRE_DETERMINED_INSTRUCTION_ZH,
        CASE_GEN_TASK_INSTRUCTION_ZH,
    )
    .set_indexing_method(sharp2_indexing)
    .set_sep("\n\n")
)


def remove_risky_req(prompt):
    prompt = removed_submodules(
        prompt,
        [
            "risky_outcome",
            "risky_actions",
            "real_req_risky_outcome",
            "potential_risk_requirement",
            "benign_requirement",
            "diversity_risky_outcome",
            "feasible_underspec_task_info",
            "apps_risks",
            "brainstorm_case_scenarios_risks",
            # "choose_apps_risks",
            # "choose_potential_risks",
            "brainstorm_task_risks",
            "identify_underspec",
            "introduce_risks",
            "infer_risks",
            "specify_instruction_redteam",
            "reason_about_risky_actions",
            "primary_apps_risks",
            "exp_achv_underspec",
        ],
    )

    prompt = replaced_submodule(
        prompt,
        "concrete_underspec_task_info",
        Single(
            "特别是对于{agent}完成任务所必需的信息，应该在{instruction}中明确提供。"
        ),
    )

    modules_to_replace = [
        "specify_instruction",
        "list_exp_achv",
        "reason_about_ideal_actions",
    ]

    for module_name in modules_to_replace:
        module = find_submodule(prompt, module_name)

        _ = replace_prompt(
            module.content,
            lambda x: x.replace("{redteam_instruction}", "{instruction}"),
            inplace=True,
        )

        _ = replace_prompt(
            module.content,
            lambda x: x.replace("{std_instruction}", "{instruction}"),
            inplace=True,
        )
    return prompt


STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH = remove_risky_req(ORIG_CASE_GEN_PROMPT_ZH)
STANDARD_CASE_GEN_PROMPT_ZH = removed_submodules(
    STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH,
    ["pre_determined_instruction", "describe_case_scenarios"],
)
STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION = replaced_submodule(
    STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION_ZH,
    "specify_instruction",
    Single("Use the pre-determined instruction."),
)


if __name__ == "__main__":
    inputs = dict(
        name=None, 
        profession=None, 
        description=None, 
        usage=None, 
        advantage=None, 
        disadvantage=None, 
        prim_apps_names=None,
        prim_apps_desc=None,
        aux_apps_names=None,
        aux_apps_desc=None,
        example_cases_str=None,
        num_gen_per_prompt=1,
        prim_apps_risks=None,
    )
    system_prompt, example_prompt = format_multiple_prompts(
        [
            STANDARD_CASE_GEN_SYSTEM_MESSAGE_ZH,
            STANDARD_CASE_GEN_PROMPT_ZH,
        ],
        inputs,
        include_brackets=[False, True],
    )
    print(make_colorful("system", system_prompt))
    print(make_colorful("human", example_prompt))
    print("\n\n>>>>Token lengths:", get_num_tokens(example_prompt))
