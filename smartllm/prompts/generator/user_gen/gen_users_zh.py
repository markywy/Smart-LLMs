from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.globals import *

GEN_USERS_SYSTEM_MESSAGE_ZH = Single(
    "你是一个细致的社会观察者，对于社会上学生、各个职位的活动和任务有着深刻了解"
)

USERS_FORMAT_ZH = NamedBlock(
    refname="app_format",
    name="Format Instructions",
    content=Sequential(
        "你必须按照下面的格式要求生成个人档案规范:",
        Collection(
            NamedBlock(
                name="Format Requirements",
                refname="format_requirements",
                content=Sequential(
                    "个人档案应该被格式化为有效的JSON字符串，并由``` JSON和```分隔。它应该包含以下字段:",
                    Collection(
                        NamedVariable(
                            refname="user_name", 
                            name="Name", 
                            content='`name`:这个人的中文名称，你可以自由想象', 
                        ), 
                        NamedVariable(
                            refname="profession", 
                            name="Profession", 
                            content='`profession`: 这个人的职业，根据要求想象', 
                        ), 
                        NamedVariable(
                            refname="user_desc", 
                            name="Description", 
                            content="`description`:包含这个人的学历、年龄、性格特点（尤其是细心程度）、对于电脑相关的知识背景、对 LLM 的熟悉程度、智能设备使用习惯，并根据 {profession}, 输出关于这个人职业的详细描述，以及人物的日常工作学习内容",
                        ), 
                        NamedVariable(
                            refname="usage", 
                            name="Usage", 
                            content="`usage`: 根据 {profession} 和 {user_desc}，生成他（她）会使用哪种几种智能体（LLM Agent）协助他（她）的工作（XXX智能体），以列表形式输出",
                        ), 
                        NamedVariable(
                            refname="advantages", 
                            name="Advantages", 
                            content="`advantages`: 从 {app} 中选定不少于 {min_apps} 个 app，根据 {profession} 和 {user_desc}，判断他（她）擅长使用哪些应用程序，将对应的应用程序名称不加改动地 **以列表形式输出**", 
                        ), 
                        NamedVariable(
                            refname="disadvantages", 
                            name="Disadvantages", 
                            content="`disadvantages`: 从 {app} 中选定不少于 {min_apps} 个 app，根据 {profession} 和 {user_desc}，判断他（她）不擅长使用哪些应用程序，将对应的应用程序名称不加改动地 **以列表形式输出**", 
                        )
                    ).set_indexing_method(number_indexing),
                ),
            ),
        )
        .set_indexing_method(sharp3_indexing)
        .set_sep("\n\n"),
    ),
)

GEN_USERS_TASK_DESC_ZH = NamedBlock(
    refname="task_desc", 
    name="Task Description", 
    content=Sequential(
        "你的任务是为以下广泛社会领域进行头脑风暴，生成现实且多样化的个人档案，用于帮助大语言模型智能体（LLM Agent）提供准确帮助：",
        "类别：{category}", 
        "类别描述：{description}", 
        "你应该遵循以下要求：", 
        Collection(
            "档案的内容包括：人物名称、职业、职业描述、性格特点（尤其是细心程度）、对于电脑相关的知识背景、对 LLM 的熟悉程度、智能设备使用习惯、日常使用的 Agent 类型、擅长使用的应用程序、不擅长使用的应用程序", 
            "生成的职业和学历覆盖全年龄，从小学生、大学在读学生到社会上主流的各种职业", 
            "确保生成的职业或学历是真实的", 
            "生成的职业或学历应具有多样性。生成工作、生活、生产需求较多的职业，涵盖不同的子类别。",
            "关注那些具有专业领域，对大部分领域没有深入了解的职业。",
            "确保日常使用的 Agent 类型与人物的生产生活存在较为紧密的联系。"
            "确保选择的应用程序名称与 {app} 完全一致，不得创造新的应用程序名称或调用未出现的子应用程序名称"
        ), 
    ).set_sep("\n"), 
)

GEN_USERS_TASK_START_ZH = NamedBlock(
    refname="start_task", 
    name="Start the task", 
    content=Sequential(
        "现在开始你的任务!你需要按照以下要求，生成 {num_gen} 个人的个人档案，以 json 形式输出：", 
        "你必须保证 json 文件中**只有一个列表**，不要把不同领域的人分开", 
        "将详细的个人档案规范合并，输出到一个 json 文件中:\n```json \n<输出个人档案的规范遵循{app_format}>\n```",
        "你必须严格坚持上述思想。特别是，在生成过程中，你不应该对上述要求进行任何简化或更改，也不应该添加任何额外的信息。",
    )
)

GEN_USERS_PROMPT_ZH = (
    Collection(GEN_USERS_TASK_DESC_ZH, USERS_FORMAT_ZH, GEN_USERS_TASK_START_ZH)
    .set_sep("\n\n")
    .set_indexing_method(sharp2_indexing)
)

if __name__ == "__main__":
    input_dict = {
        "category": "{category}",
        "description": "{description}",
        "num_gen": "{num_gen}",
        "min_apps" : "{min_apps}", 
        "app": "{app}", 
    }
    print(format_prompt(GEN_USERS_PROMPT_ZH, input_dict))