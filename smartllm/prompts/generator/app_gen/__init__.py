from procoder.prompt import Module as PromptModule

from .gen_app_names import GEN_NAMES_PROMPT, GEN_NAMES_SYSTEM_MESSAGE
from .gen_app_names_zh import GEN_NAMES_PROMPT_ZH, GEN_NAMES_SYSTEM_MESSAGE_ZH
from .gen_app_specs import GEN_APP_SPEC_PROMPT, GEN_APP_SPEC_SYSTEM_MESSAGE
from .gen_app_specs_zh import GEN_APP_SPEC_PROMPT_ZH, GEN_APP_SPEC_SYSTEM_MESSAGE_ZH
from .risky import (
    RISKY_APP_GEN_BRAINSTORMED_PROMPT,
    RISKY_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT,
    RISKY_APP_GEN_FIXED_PROMPT,
    RISKY_APP_GEN_FIXED_THOUGHTS_PROMPT,
)
from .risky_zh import (
    RISKY_APP_GEN_BRAINSTORMED_PROMPT_ZH,
    RISKY_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH,
    RISKY_APP_GEN_FIXED_PROMPT_ZH,
    RISKY_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH,
)
from .shared import APP_GEN_SYSTEM_MESSAGE
from .shared_zh import APP_GEN_SYSTEM_MESSAGE_ZH
from .standard import (
    STD_APP_GEN_BRAINSTORMED_PROMPT,
    STD_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT,
    STD_APP_GEN_FIXED_PROMPT,
    STD_APP_GEN_FIXED_THOUGHTS_PROMPT,
)
from .standard_zh import (
    STD_APP_GEN_BRAINSTORMED_PROMPT_ZH,
    STD_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH,
    STD_APP_GEN_FIXED_PROMPT_ZH,
    STD_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH,
)
APP_GEN_PROMPTS = {
    "std_fixed": STD_APP_GEN_FIXED_PROMPT,
    "std_brainstorm": STD_APP_GEN_BRAINSTORMED_PROMPT,
    "std_fixed_thoughts": STD_APP_GEN_FIXED_THOUGHTS_PROMPT,
    "std_brainstorm_thoughts": STD_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT,
    "risky_fixed": RISKY_APP_GEN_FIXED_PROMPT,
    "risky_brainstorm": RISKY_APP_GEN_BRAINSTORMED_PROMPT,
    "risky_fixed_thoughts": RISKY_APP_GEN_FIXED_THOUGHTS_PROMPT,
    "risky_brainstorm_thoughts": RISKY_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT,
}
APP_GEN_PROMPTS_ZH = {
    "std_fixed": STD_APP_GEN_FIXED_PROMPT_ZH,
    "std_brainstorm": STD_APP_GEN_BRAINSTORMED_PROMPT_ZH,
    "std_fixed_thoughts": STD_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH,
    "std_brainstorm_thoughts": STD_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH,
    "risky_fixed": RISKY_APP_GEN_FIXED_PROMPT_ZH,
    "risky_brainstorm": RISKY_APP_GEN_BRAINSTORMED_PROMPT_ZH,
    "risky_fixed_thoughts": RISKY_APP_GEN_FIXED_THOUGHTS_PROMPT_ZH,
    "risky_brainstorm_thoughts": RISKY_APP_GEN_BRAINSTORMED_THOUGHTS_PROMPT_ZH,
}

def get_app_gen_prompt(
    gen_risky_tool: bool, brainstorm: bool, thoughts_only: bool = True
) -> PromptModule:
    name = ["risky" if gen_risky_tool else "std"]
    name.append("brainstorm" if brainstorm else "fixed")
    if thoughts_only:
        name.append("thoughts")
    return APP_GEN_PROMPTS["_".join(name)]

def get_app_gen_prompt_zh(
    gen_risky_tool: bool, brainstorm: bool, thoughts_only: bool = True
) -> PromptModule:
    name = ["risky" if gen_risky_tool else "std"]
    name.append("brainstorm" if brainstorm else "fixed")
    if thoughts_only:
        name.append("thoughts")
    return APP_GEN_PROMPTS_ZH["_".join(name)]