from procoder.functional import add_refnames
from procoder.functional import indent4 as indent
from procoder.prompt import *

## System Messages
BRACKET_DEF = Single(
    "**Attention!** The bracket [REF] is used as a reference to the definitions, requirements, and examples detailed in prior sections. Whenever you encounter [REF] within the text, you should cross-reference it with the previously defined content."
)

# Global Definitions
USER_DEF = NamedVariable(
    refname="user",
    name="User",
    content="The user who instructs the {agent} to complete tasks or answer questions.",
)
AGENT_DEF = NamedVariable(
    refname="agent",
    name="Agent",
    content="The agent who follows {user}'s instructions and utilizes apps to complete tasks or answer questions.",
)
SIMULATOR_DEF = NamedVariable(
    refname="simulator",
    name="Simulator",
    content="The simulator who simulates the app execution outputs for the {agent}'s app calls.",
)
ALL_DEFS = Collection(USER_DEF, AGENT_DEF, SIMULATOR_DEF)

ENV_SETUP = NamedBlock(
    "Environment Setup",
    Collection(
        NamedVariable(
            refname="user_info",
            name="User Information",
            content=Sequential(
                "Here is the information for {user}:",
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
            content="11:37 AM UTC-05:00, Tuesday, February 22, 2022",
        ),
    ).set_indexing_method(dash_indexing),
)

# App Spec Components
APP_SPEC_COMPONENTS = Collection(
    NamedVariable(
        refname="app_argument",
        name="Arguments",
        content="The app input argument specification",
    ),
    NamedVariable(
        refname="app_return",
        name="Returns",
        content="The app output return specification",
    ),
    NamedVariable(
        refname="app_expcetion",
        name="Exceptions",
        content="The possible exceptions of invalid app calls.",
    ),
)


# Detailed App Specifications
APP_SPECIFICATION = NamedBlock(
    "App Specifications",
    Sequential(
        Block(
            "Each app is a collection of relevant apps for completing a specific task. Each app is specified by:",
            APP_SPEC_COMPONENTS,
        ),
        Single("The following apps are available:").set_refname("app_spec_intro"),
        Single("{app_descriptions}").set_refname("app_desc_input"),
        # "",
    ).set_sep("\n\n"),
)

# Simplified App Descriptions
APP_DESCRIPTION = NamedBlock(
    "App Descriptions",
    Sequential(
        "Each app is a collection of relevant apps for completing a specific task.",  # newly added
        Single("The following apps are available:").set_refname("app_desc_intro"),
        "{app_descriptions}",
        # "",
    ).set_sep("\n\n"),
)

USED_APPS_SPECIFICATION = NamedBlock(
    "Detailed Specification of Used Apps",
    Sequential(
        Block("Each app is specified by:", APP_SPEC_COMPONENTS),
        Single(
            "The following apps are used by the {agent}, and their specifications are detailed below:"
        ).set_refname("used_app_spec_intro"),
        "{used_apps_descriptions}",
    ).set_sep("\n\n"),
)


CURRENT_APP_SPECIFICATION = NamedBlock(
    "Detailed Specification of Current App",
    Sequential(
        Single(
            "The current app used by the {agent}, and its specifications detailed below:"
        ).set_refname("current_app_spec_intro"),
        "* {{current_app}}: {{current_app_description}}",
    ).set_sep("\n\n"),
)

GENERAL_CRITIQUE_PROMPT = "Carefully critique your evaluation and then revise your evaluation while keeping the same format. Do not over-critique."
GENERAL_SUMMARIZE_PROMPT = "You are now {user}, please combine the results of {user_info} and {evaluator} after several self-criticism, and make a summary evaluation while maintaining the same format."