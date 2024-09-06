from procoder.functional import collect_refnames, format_multiple_prompts
from procoder.functional import indent4 as indent
from procoder.functional import removed_submodules, replaced_submodule
from procoder.prompt import *
from smartllm.prompts.agent.shared_zh import *
from smartllm.prompts.globals_zh import *
from smartllm.prompts.principles_zh import (
    APP_CALL_HELPFULNESS_REQS_ZH,
    APP_CALL_SAFETY_SECURITY_REQS_ZH,
)
from smartllm.utils import get_num_tokens, make_colorful

AGENT_HELPFUL_SS_SYSTEM_INFO_ZH = AGENT_SYSTEM_INFO_ZH

AGENT_HELPFUL_SS_REQS_ZH = NamedBlock(
    "Requirement Checklist",
    Collection(APP_CALL_HELPFULNESS_REQS_ZH, APP_CALL_SAFETY_SECURITY_REQS_ZH)
    .set_indexing_method(sharp3_indexing)
    .set_sep("\n\n"),
)

AGENT_HELPFUL_SS_PROMPT_ZH = (
    Collection(
        AGENT_ENV_SETUP_ZH,
        AGENT_TASK_DESC_ZH,
        AGENT_FORMAT_INSTRUCTION_ZH,
        AGENT_HELPFUL_SS_REQS_ZH,
        AGENT_TASK_BEGIN_ZH,
    )
    .set_indexing_method(sharp2_indexing)
    .set_sep("\n\n")
)

AGENT_HELPFUL_SS_PROMPT_ZH = replace_agent_ref_with_pronoun(AGENT_HELPFUL_SS_PROMPT_ZH)

AGENT_HELPFUL_SS_CLAUDE_PROMPT_ZH = replaced_submodule(
    AGENT_HELPFUL_SS_PROMPT_ZH, "task_begin", AGENT_TASK_BEGIN_FOR_CLAUDE_ZH
)


if __name__ == "__main__":
    inputs = dict(
        app_descriptions=None, 
        tool_names=None, 
        name=None, 
        profession=None, 
        description=None, 
        usage=None, 
        advantage=None, 
        disadvantage=None, 
    )
    add_refnames(AGENT_DUMMY_VARS_ZH, inputs, include_brackets=False)
    system_prompt, example_prompt = format_multiple_prompts(
        [
            AGENT_HELPFUL_SS_SYSTEM_INFO_ZH,
            AGENT_HELPFUL_SS_PROMPT_ZH,
        ],
        inputs,
        include_brackets=[False, True],
    )
    print(make_colorful("system", system_prompt))
    print(make_colorful("human", example_prompt))
    print("\n\n>>>>Token lengths:", get_num_tokens(example_prompt))
