from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.generator.app_gen.shared import *
from smartllm.utils import JSON_TYPES_STR

GEN_APP_SPEC_SYSTEM_MESSAGE_ZH = Single(
    "你是一个熟练的应用程序生成专家，熟练地按照格式说明和示例精心创建应用程序规格。",
)

GEN_APP_SPEC_GENERAL_TASK_DESC_ZH = NamedBlock(
    name="Task Description",
    refname="general_task_desc",
    content=Sequential(
        "你的目标是创建全面的应用程序规范。你已经掌握了应用程序的开发思想，你的任务是将其转换为JSON应用程序规范。",
        "应用程序规范要一丝不苟地坚持开发思想，格式要按照下面的说明和示例进行。",
    ).set_sep(" "),
)


GEN_APP_SPEC_TASK_START_ZH = NamedBlock(
    name="Start the Task",
    refname="start_task",
    content=Sequential(
        "现在开始你的任务!你会得到以下的开发思路:",
        "```\n{development_thought}\n```",
        "将上述思想转换为JSON应用程序规范. 将详细的应用程序规范输出为:\n```json\n<the output app specification follows the {app_format}>\n```",
        "你必须包含backsticks并遵循规范结构{format_example}。你应该为每个应用指定详细的描述，并精确地包括应用描述的所有必要信息(例如，可选参数的默认值，格式约束，值约束，对象参数或返回中每个字段的详细描述，等等)。",
        "你必须严格坚持上述思想。特别是，在开发思想中，你不应该对描述进行任何简化或更改，也不应该添加任何额外的信息。",
    ),
)

GEN_APP_SPEC_PROMPT_ZH = (
    Collection(GEN_APP_SPEC_GENERAL_TASK_DESC_ZH, APP_FORMAT, GEN_APP_SPEC_TASK_START_ZH)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing)
)

if __name__ == "__main__":
    input_dict = {
        "development_thought": "{development_thought}",
        "json_types": JSON_TYPES_STR,
        "examples": "{format_example}",
    }
    print(format_prompt(GEN_APP_SPEC_PROMPT_ZH, input_dict))
