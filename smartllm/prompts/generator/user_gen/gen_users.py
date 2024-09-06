from procoder.functional import *
from procoder.functional import indent4 as indent
from procoder.prompt import *
from smartllm.prompts.globals import *

GEN_USERS_SYSTEM_MESSAGE = Single(
    "You are a meticulous observer of society and have a deep understanding of the activities and tasks of students and various positions in society."
)

USERS_FORMAT = NamedBlock(
    refname="app_format",
    name="Format Instructions",
    content=Sequential(
        "You must generate the profile specification in the following format:",
        Collection(
            NamedBlock(
                name="Format Requirements",
                refname="format_requirements",
                content=Sequential(
                    "The profile should be formatted as a valid JSON string, separated by ' ' 'JSON and' ' '. It should contain the following content:",
                    Collection(
                        NamedVariable(
                            refname="user_name", 
                            name="Name", 
                            content='`name`:Name of the person, which you can imagine freely.', 
                        ), 
                        NamedVariable(
                            refname="profession", 
                            name="Profession", 
                            content='`profession`: Profession of the person, which you should imagine as required.', 
                        ), 
                        NamedVariable(
                            refname="user_desc", 
                            name="Description", 
                            content="`description`:Includes the person's education background, age, personality characteristics (especially careful degree), knowledge background related to computer, familiarity with llm, and habit of using smart devices. According to {profession}, it outputs a detailed description of the person's occupation, as well as the person's daily work and study content.",
                        ), 
                        NamedVariable(
                            refname="usage", 
                            name="Usage", 
                            content="`usage`: According to {profession} and {user_desc}, generate which kinds of agents (LLM agents) he or she will use to assist him or her in his or her work (XXX agents), and output in a list form",
                        ), 
                        NamedVariable(
                            refname="advantages", 
                            name="Advantages", 
                            content="`advantages`: Choose no less than {min_apps} apps from {app}, based on {profession} and {user_desc}, determine which app he or she is good at using, and **print out the corresponding app names as a list** unchangeably", 
                        ), 
                        NamedVariable(
                            refname="disadvantages", 
                            name="Disadvantages", 
                            content="`disadvantages`: Choose no less than {min_apps} apps from {app}, based on {profession} and {user_desc}, determine which app he or she is not good at using, and **print out the corresponding app names as a list** unchangeably", 
                        )
                    ).set_indexing_method(number_indexing),
                ),
            ),
        )
        .set_indexing_method(sharp3_indexing)
        .set_sep("\n\n"),
    ),
)

GEN_USERS_TASK_DESC = NamedBlock(
    refname="task_desc", 
    name="Task Description", 
    content=Sequential(
        "Your task is to brainstorm realistic and diverse profiles for the following broad social domains, which can be used to accurately assist large Language Model agents (LLM agents) : ",
        "Category: {category}",
        "Category description: {description}",
        "You should follow these requirements: ",
        Collection(
            "The contents of the file include: name of the person, occupation, occupation description, personality characteristics (especially the degree of carefulness), knowledge background related to computer, familiarity with LLM, habit of using smart devices, types of agents used daily, apps that are good at using, apps that are not good at using", 
            "The generated professions and degrees cover all ages, from primary school students, university students to mainstream professions in society", 
            "Make sure the generated occupation or degree is authentic", 
            "The generated professions or degrees should be diverse. professions with more work, life, and production demands are generated, covering different subcategories.",
            "Focus on professions that have areas of expertise and don't have in-depth knowledge of most areas.",
            "Ensure that the types of agents used in daily life are closely related to the production and life of characters."
            "Make sure that the app name you select is exactly the same as {app}, and do not create new app names or invoke sub-app names that do not appear"
        ), 
    ).set_sep("\n"), 
)

GEN_USERS_TASK_START = NamedBlock(
    refname="start_task", 
    name="Start the task", 
    content=Sequential(
        "Now start your task! You need to generate a {num_gen} profile for each individual and output it as json:", 
        "You must ensure there is **only one** list in json file, don't devide the person from different fields to diffrent lists.", 
        "The detailed profile specifications are outputted together into only one json file:\n```json(lowercase) \n<output profile specifications follow {app_format}>\n",
        "You must strictly adhering to the above thoughts. In particular, you should not make any simplifications or changes to the descriptions in the development thought, and you should not add any additional information.",
    )
)

GEN_USERS_PROMPT = (
    Collection(GEN_USERS_TASK_DESC, USERS_FORMAT, GEN_USERS_TASK_START)
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
    print(format_prompt(GEN_USERS_PROMPT, input_dict))