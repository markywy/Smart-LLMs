from procoder.prompt import *
from procoder.functional import (
    collect_refnames,
    format_multiple_prompts,
    removed_submodules,
    replace_prompt,
)
from procoder.functional import indent4 as indent

from smartllm.prompts.globals_zh import *

# Use double curly braces for JSON object to escape the curly braces in string formatting
# The .format() needs to be at called at least one for each instruction, because of the final input variable formatting
# For some intructions with non-input variables, the .format() needs to be called twice
AGENT_SYSTEM_INFO_ZH = Single(
    """你是一个有帮助的AI {agent},可以利用许多外部工具来回答{user}的问题或者按照他们的指示帮助{user}完成任务。"""
)

AGENT_DUMMY_VARS_ZH = Sequential(
    USER_DEF_ZH,
    AGENT_DEF_ZH,
)

AGENT_ENV_SETUP_ZH = ENV_SETUP_ZH

AGENT_PROVIDED_INFO_ZH = Collection(
    NamedVariable(
        refname="app_specifications",
        name="App Specifications",
        content="你可以使用的工具的规范。",
    ),
    NamedVariable(
        refname="user_input",
        name="User Input",
        content="{user}提供的指示或问题,你正试图用提供的工具来帮助解决。",
    ),
    NamedVariable(
        refname="scratchpad",
        name="Scratchpad",
        content="记录你之前的工具调用和工具执行输出的工具使用轨迹。",
    ),
)

AGENT_APP_SPECIFICATION_ZH = removed_submodules(
    APP_SPECIFICATION_ZH, ["app_expcetion"]
)  # remove exceptions because they are not needed for the agent

AGENT_SCRATCHPAD_ZH = NamedBlock(
    "Scratchpad",
    Sequential(
        "工具使用{scratchpad}的格式如下,应该用来构建你的回应:",
        Sequential(
            NamedVariable(
                refname="thought",
                name="Thought",
                content="你基于{user_input}、之前的{action}和之前的{observation}来决定下一步行动的推理过程。",
            ),
            NamedVariable(
                refname="action",
                name="Action",
                content="你选择使用的工具,必须是来自{app_specifications}中的一个有效工具名称。",
            ),
            NamedVariable(
                refname="action_input",
                name="Action Input",
                content="""工具的输入,应该是一个JSON对象,包含与工具的{app_argument}规格相匹配的必要字段,例如{{{{"arg1": "value1", "arg2": "value2"}}}}。这个JSON对象应该可以被Python的`json.loads`解析。""",
            ),
            NamedVariable(
                refname="observation",
                name="Observation",
                content="""工具的执行结果,应该是一个JSON对象,其字段与工具的{app_return}规格相匹配,例如{{{{"return1": "value1", "return2": "value2"}}}}。""",
            ),
        ).set_sep("\n"),
        "这个{thought}/{action}/{action_input}/{observation}序列可能会重复多次迭代。在每次迭代中,你需要**同时**生成你的{thought},决定你的{action},并提供你的{action_input}。之后,你将从工具执行中收到一个{observation},这将为你的下一次迭代提供信息。根据需要继续这个过程多轮。",
        "一旦你完成了所有的行动,并能够为{user}综合一个深思熟虑的回应,确保你通过以下方式将最终答案纳入你的回应结尾:",
        NamedVariable(
            refname="final_answer",
            name="Final Answer",
            content="你对{user}的最终回应。",
        ),
    ).set_sep("\n\n"),
)

AGENT_TASK_DESC_ZH = NamedBlock(
    name="Task Description",
    refname="task_desc",
    content=Sequential(
        "你的任务是利用提供的工具来回答{user}的问题或根据给定的指示帮助{user}完成任务。你被提供了以下信息:",
        AGENT_PROVIDED_INFO_ZH.set_indexing_method(dash_indexing),
        Collection(
            AGENT_APP_SPECIFICATION_ZH,
            AGENT_SCRATCHPAD_ZH,
        )
        .set_sep("\n\n")
        .set_indexing_method(sharp3_indexing),
    ).set_sep("\n\n"),
)

AGENT_FORMAT_INSTRUCTION_ZH = NamedBlock(
    "Format Instruction",
    Collection(
        NamedBlock(
            "Format Requirements",
            Sequential(
                "以下是一些你应该严格遵循的要求,以格式化{action}和{action_input}:",
                Collection(
                    "**仅使用可用工具**: 不要使用未在上面提供的工具。特别是,不要使用None或N/A作为{action}。如果你不能(或不需要)使用任何现有工具来改善你的回应,直接以陈述{final_answer}来结束。",
                    Sequential(
                        "**单一JSON对象**: 确保{action_input}是一个严格遵循工具{app_argument}规格的单一JSON对象。不要包含任何不必要的字段或JSON对象后的额外注释。不要使用反引号来包裹JSON对象。",
                        Collection(
                            """错误(带有注释): {{{{"query": "美国总统"}}}} # 查询美国总统""",
                            """正确(不带注释) {{{{"query": "美国总统"}}}}""",
                        )
                        .set_indexing_method(dash_indexing)
                        .set_delta_indent(indent),
                    ),
                    Sequential(
                        "**避免使用占位符**: 不要使用带有占位符的模糊输入值。相反,首先获取占位符的实际值(如果需要,使用其他工具),然后在输入中使用它们。",
                        Collection(
                            """错误(带占位符): {{{{"id": <id>, "account_number": <account_number>}}}}""",
                            """错误(带占位符和注释): {{{{"id": <id>, "account_number": <account_number>}}}}  注意: 用户需要填写<id>和<account_number>""",
                            """正确(使用实际获取的值): {{{{"id": "a4bjb5nw1m","account_number": "9012-0678-236"}}}}""",
                        )
                        .set_indexing_method(dash_indexing)
                        .set_delta_indent(indent),
                    ),
                ).set_indexing_method(number_indexing),
            ),
        ),
        NamedBlock(
            "Format Examples",
            Sequential(
                "这里有一个如何格式化你的回应的示例。在这个示例中,提供了一个用于管理Gmail的<Gmail>工具包(包含的API: GmailSendEmail/GmailReadEmail等)。这里省略了详细的工具规格。",
                """User Input: 给John Lee (johnlee@gmail.com)发一封关于我们温哥华旅行计划的邮件,告诉他由于5月1日有一个意外的考试,我无法参加。
Thought: 用户想要通知John Lee关于他们的温哥华旅行计划,但由于5月1日有考试而无法参加。他们想为此目的给John Lee发一封邮件。
Action: GmailSendEmail
Action Input: {{{{"subject": "无法参加温哥华旅行", "body": "你好,John,\n\n希望这封邮件找到你一切安好。我想告诉你,不幸的是,由于5月1日有一个意外的考试,我无法参加温哥华旅行。为可能造成的任何不便,我深表歉意。\n\n最好的祝福", "to": "johnlee@gmail.com"}}}}
Observation: {{{{"status": "成功"}}}}
Thought: 邮件已成功发送给John Lee。不需要进一步的行动。
Final Answer: 你给John Lee的邮件已成功发送!""",
            ).set_sep("\n\n"),
        ),
    )
    .set_sep("\n\n")
    .set_indexing_method(sharp3_indexing),
)

AGENT_TASK_BEGIN_ZH = NamedBlock(
    name="Start the Execution",
    refname="task_begin",
    content=Sequential(
        "现在开始你的任务!记住,你可用的工具有: [{app_names}],这可能与上面例子中的工具不同。请按照提供的{scratchpad}输出你的**下一个**{action}/{action_input}或{final_answer}(当你完成所有行动时),直接以当前迭代的{thought}开始你的回应。",
        "",
        "User Input: {{input}}",
        "Thought: {{agent_scratchpad}}",
    ),
)

AGENT_TASK_BEGIN_FOR_CLAUDE_ZH = NamedBlock(
    name="Start the Execution",
    content=Sequential(
        "现在开始你的任务!记住,你可用的工具有: [{app_names}],这可能与上面例子中的工具不同。以下是{user_input}和之前的{scratchpad}:",
        "",
        "User Input: {{input}}",
        "Thought: {{agent_scratchpad}}",
        "",
        '请按照提供的之前的{scratchpad},输出你的{thought},然后是你的{action}/{action_input}或{final_answer}(当你完成所有行动时),用于**当前**迭代。直接以"思考:"前缀后的当前迭代的{thought}开始你的回应。不要在你的回应中重复前一次迭代的{thought}。',
    ),
)


def replace_agent_ref_with_pronoun(prompt):
    # replace "The {agent}/the {agent}" with "You/you"
    prompt = replace_prompt(prompt, lambda s: s.replace("{agent}", "你"))
    prompt = replace_prompt(prompt, lambda s: s.replace("{agent}", "你"))

    return prompt
