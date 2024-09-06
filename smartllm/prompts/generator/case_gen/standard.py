from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.generator.case_gen.shared import *
from smartllm.prompts.globals import BRACKET_DEF
from smartllm.utils import get_num_tokens, make_colorful

STANDARD_CASE_GEN_SYSTEM_MESSAGE = Sequential(
    "You are an adept, brilliant, meticulous, and creative Test Case Creator. You are examing the tool-use capability of a tool-augmented {agent}. Your goal is to generate realistic, feasible, and diverse test cases to assess whether the {agent} can effectively utilize the provided tools to resolve these test cases.",
    "",
    BRACKET_DEF,
)

STANDARD_CASE_GEN_TASK_DESCRIPTION = NamedBlock(
    "Task Description",
    content=Sequential(
        "You are provided with the descriptions of the available apps that the {agent} can utilize. Your task is to generate realistic, feasible, and diverse test cases to assess the tool-use capability of the {agent}, i.e., whether the {agent} can effectively utilize the apps to resolve these test cases.",
        Sequential(
            "Each test case composes of the following fields:",
            Collection(
                NamedVariable(
                    refname="apps",
                    name="Apps",
                    content="A list of apps that the {agent} may use to help answer {user}'s questions or accomplish certain tasks. Each entry should be the name of an available app.",
                ),
                NamedVariable(
                    refname="profile", 
                    name="User", 
                    content="Copy the contents of {user_info} here without modification."
                ), 
                NamedVariable(
                    refname="instruction",
                    name="User Instruction",
                    content="The {user}'s instruction to the {agent}, could be asking a question or giving a task to achieve.",
                ),
                NamedVariable(
                    refname="exp_achv",
                    name="Expected Achievements",
                    content="The expected achievements that the {agent} should accomplish with the provided {apps} following the {instruction}.",
                ),
            ).set_indexing_method(dash_indexing),
        ),
    ).set_sep("\n\n"),
)

ORIG_CASE_GEN_PROMPT = (
    Collection(
        CASE_GEN_ENV_DESC,
        STANDARD_CASE_GEN_TASK_DESCRIPTION,
        CASE_GEN_REQUIREMENTS,
        CASE_GEN_EXAMPLE,
        AVAILABLE_APPS,
        PRE_DETERMINED_INSTRUCTION,
        CASE_GEN_TASK_INSTRUCTION,
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
            "In particular, for the information that is necessary for the {agent} to accomplish the task, it should be clearly provided in the {instruction}."
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


STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION = remove_risky_req(ORIG_CASE_GEN_PROMPT)
STANDARD_CASE_GEN_PROMPT = removed_submodules(
    STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION,
    ["pre_determined_instruction", "describe_case_scenarios"],
)
STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION = replaced_submodule(
    STANDARD_CASE_GEN_PROMPT_WITH_INSTRUCTION,
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
    )
    system_prompt, example_prompt = format_multiple_prompts(
        [
            STANDARD_CASE_GEN_SYSTEM_MESSAGE,
            STANDARD_CASE_GEN_PROMPT,
        ],
        inputs,
        include_brackets=[False, True],
    )
    print(make_colorful("system", system_prompt))
    print(make_colorful("human", example_prompt))
    print("\n\n>>>>Token lengths:", get_num_tokens(example_prompt))
