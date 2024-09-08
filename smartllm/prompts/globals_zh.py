from procoder.functional import add_refnames, format_prompt
from procoder.functional import indent4 as indent
from procoder.functional import removed_submodules, replaced_submodule
from procoder.prompt import *
from smartllm.utils import get_num_tokens, make_colorful

## System Messages
BRACKET_DEF_ZH = Single(
    "**注意！** 方括号 [REF] 用作参考，指向前面章节中详细说明的定义、要求和示例。每当您在文本中看到 [REF] 时，应该将其与之前定义的内容进行交叉引用。"
)

# Global Definitions
USER_DEF_ZH = NamedVariable(
    refname="user",
    name="User",
    content="指示 {agent} 完成任务或回答问题的用户。",
)
AGENT_DEF_ZH = NamedVariable(
    refname="agent",
    name="Agent",
    content="遵循 {user} 的指令并使用应用来完成任务或回答问题的 {agent}。",
)
SIMULATOR_DEF_ZH = NamedVariable(
    refname="simulator",
    name="Simulator",
    content="模拟 {agent} 应用调用的应用执行输出的模拟器。",
)
ALL_DEFS_ZH = Collection(USER_DEF_ZH, AGENT_DEF_ZH, SIMULATOR_DEF_ZH)

ENV_SETUP_ZH = NamedBlock(
    "Environment Setup",
    Collection(
        NamedVariable(
            refname="user_info",
            name="User Information",
            content=Sequential(
                "以下是 {user} 的信息：",
                Collection(
                    NamedVariable(
                        refname="user_name",
                        name="Name",
                        content="{name}",
                    ),
                    NamedVariable(
                        refname="user_profession", 
                        name="Profession",  
                        content="{profession}", 
                    ), 
                    NamedVariable(
                        refname="user_desc", 
                        name="Description", 
                        content="{description}",
                    ), 
                    NamedVariable(
                        refname="user_usage", 
                        name = "Usage", 
                        content=Sequential(
                            "", 
                            Collection(
                                "{usage}", 
                            ).set_indexing_method(dash_indexing)
                                .set_delta_indent(indent),
                        ), 
                    ), 
                    NamedVariable(
                        refname="user_advantages", 
                        name="Advantages", 
                        content=Sequential(
                            Collection(
                                "{advantage}"
                            ).set_indexing_method(dash_indexing)
                                .set_delta_indent(indent),
                        ), 
                    ), 
                    NamedVariable(
                        refname="user_disadvantages", 
                        name="Disadvantages", 
                        content=Sequential(
                            Collection(
                                "{disadvantage}"
                            ).set_indexing_method(dash_indexing)
                                .set_delta_indent(indent),
                        ), 
                    ), 
                    NamedVariable(
                        refname="user_email",
                        name="Email",
                        content="somebody@gmail.com",
                    ),
                )
                .set_indexing_method(dash_indexing)
                .set_delta_indent(indent),
            ),
        ),
        NamedVariable(
            refname="cur_time",
            name="Current Time",
            content="上午 11:37，UTC-05:00, 2022 年 2 月 22 日，星期二",
        ),
    ).set_indexing_method(dash_indexing),
)

# App Spec Components
APP_SPEC_COMPONENTS_ZH = Collection(
    NamedVariable(
        refname="app_argument",
        name="Arguments",
        content="应用输入参数规范",
    ),
    NamedVariable(
        refname="app_return",
        name="Returns",
        content="应用输出返回规范",
    ),
    NamedVariable(
        refname="app_expcetion",
        name="Exceptions",
        content="无效应用调用的可能异常",
    ),
)


# Detailed App Specifications
APP_SPECIFICATION_ZH = NamedBlock(
    "App Specification",
    Sequential(
        Block(
            "每个应用程序是完成特定任务的相关应用的集合。每个应用由以下内容指定：",
            APP_SPEC_COMPONENTS_ZH,
        ),
        Single("以下应用可用：").set_refname("app_spec_intro"),
        Single("{app_descriptions}").set_refname("app_desc_input"),
        # "",
    ).set_sep("\n\n"),
)

# Simplified App Descriptions
APP_DESCRIPTION_ZH = NamedBlock(
    "App Description",
    Sequential(
        "每个应用程序是完成特定任务的相关应用的集合。",  # newly added
        Single("以下应用可用：").set_refname("app_desc_intro"),
        "{app_descriptions}",
        # "",
    ).set_sep("\n\n"),
)

USED_APPS_SPECIFICATIO_ZH = NamedBlock(
    "Detailed Specification of Used Apps",
    Sequential(
        Block("每个应用由以下内容指定：", APP_SPEC_COMPONENTS_ZH),
        Single(
            "以下应用由 {agent} 使用，其规范详述如下："
        ).set_refname("used_app_spec_intro"),
        "{used_apps_descriptions}",
    ).set_sep("\n\n"),
)


CURRENT_APP_SPECIFICATION_ZH = NamedBlock(
    "当前应用的详细规范",
    Sequential(
        Single(
            "当前由 {agent} 使用的应用及其详细规范如下："
        ).set_refname("current_app_spec_intro"),
        "* {{current_app}}: {{current_app_description}}",
    ).set_sep("\n\n"),
)

GENERAL_CRITIQUE_PROMPT_ZH = "仔细批评您的评估，然后在保持相同格式的情况下修订您的评估。不要过度批评。"

GENERAL_SUMMARIZE_PROMPT_ZH = "你现在是 {user}，请结合自身情况 {user_info} 与 {evaluator} 经过若干次自我批判的结果, 在保持相同格式的情况下做出总结性评估"