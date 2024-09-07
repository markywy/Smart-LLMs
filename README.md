# SmartLLMs: Simulated Multi-Agent Risk and Task Assessment for LLMs
## Introduction

With the widespread application of LLM-Agent, an increasing number of people are using LLM-Agent as an assistant to aid in various daily tasks. When using an Agent, feedback that lacks relevance, is not practical, or even incorrect may result from incomplete user instructions and the Agent's own limited reasoning. Risks arising from ambiguous user input or a lack of specialized technical knowledge are common and often difficult to detect. Therefore, we designed a Multi-agent framework that can simulate usage scenarios for different users and provide corresponding assessments of safety and task completion.

## SmartLLMs

Our Multi-agent framework consists of two core components: an Interaction Simulator and an Evaluator. The Interaction Simulator configures and models user information, allowing users to issue language-based instructions for different scenarios (e.g., booking a flight). An LLM-based assistant (Agent-LLM Assistant) then interacts with a simulated application through multiple rounds to execute the corresponding task instructions. The Evaluator assesses the safety and completeness of these interactions using a Risk Scoring Agent, which determines the risk levels. Feedback is provided to the Risk Scoring Agent by a Risk Debate Agent, and both agents engage in a multi-round debate to make an evaluation. Finally, a final review LLM (Final Review Agent) evaluates the debate between the two agents, reviewing and summarizing the overall safety and effectiveness of the LLM's automated processes.

![Framework](assets\figures\Framework.jpg)

## Content

This manual contains:

* [Generating your own virtual apps, users and usage cases with LLM]
  
* [Customizing the simulation environment and conducting simulations.]

* [Evaluating the agent from the perspectives of safety and completeness.]

## Preparations
### Installation
In this framework, we need a module called [PromptCoder](https://github.com/dhh1995/PromptCoder) to edit and format the message. Run the command below to get the complete respositories and modules:

```bash
# Get the repositories
git clone https://github.com/dhh1995/PromptCoder.git
git clone https://github.com/markywy/SmartLLMs.git

# Install the modules
cd PromptCoder
pip install -e .
cd .SmartLLMs
pip install -e .
```
### Add your API keys

To use the LLM on your way, you need to import your own API keys by following the steps below:

1. Make the file `.env` at the directory `/SmartLLMs`
2. Input a single line `OPENAI_API_KEY=<Your Openai API Keys>` in file `.env`
3. If you want to use the model `Claude`, use `AUANTHROPIC_API_KEY=`
4. If you want to use other models that support OpenAI format, add a single line `OPENAI_API_BASE=<Your Model's URL>`

## Get Start
### Hint

1. Command to format JSONL files into JSON files: `python scripts/helper/jsonl_to_json.py <file_path_to_convert>`. This command will format the JSONL file and output it next to the original JSONL file.

2. All scripts (.py files) are located in `scripts`.


### Generating your own virtual apps, users and usage cases with LLM

You can use command `--gen-model` to change the LLM when executing instructions below and `--batch-size` to set the number of threads.

#### Generating Applications

1. Ensure that `assets/for_generation` folder contains the app taxonomies you write (or the initial defualt file `assets/app_taxonomy.json`). 

2. Generate the name of the applications with `gen_app_names.py`: `python scripts/generation/gen_app_names.py -inp assets/for_generation/app_taxonomy.json`.

3. Generate the LLM thoughts (potential risks, risk actions, etc.) of the applications with `gen_app_thoughts.py`: `python scripts/generation/gen_app_thoughts.py -inp <file_path_from_step_1>`.

4. Generate the specification of the applications with `gen_app_specs.py`: `python scripts/generation/gen_app_specs.py -inp <file_path_from_step_2>`.

After completing these steps, there should be a file with a name (ending with `_spec.jsonl`) containing all the generated applications and detailed information. You can use `jsonl_to_json.py` to convert this file into `json` format and save it.

#### Generating Users

0. Ensure that `assets/for_generation` folder contains `user_taxonomy.json`.

1. Generate user profiles with `gen_users.py`: `python scripts/generation/gen_users.py -inp assets/for_generation/user_taxonomy.json -ap <application_file_path>`.

After completing this step, a file named `gen_users.jsonl` will be generated, containing information about all users. You can use `jsonl_to_json.py` to convert this file into `json` format and save it.

#### Generating Cases

1. **(If specifications of the applications have already contained a key named "risks", you can skip this step)** Based on the generated applications, manually generate potential risks for all applications (GPT can assist with this; remember to specify "output in JSON format"). Store this in `assets/for_generation/applications_risks.json`.

2. Generate the usage cases with `gen_test_cases.py`: `python scripts/generation/gen_test_cases.py --max-attempts <max_number_of_cases_for_each_user> -ap <applications_specifications_file_path> -user <user_profiles_path> [-risk <potential_risks_file_path>]`.

After completing this step, a file named `gen_cases_<timestamp>.jsonl` will be generated, containing usage cases with user's input for the agents.

### Customizing the simulation environment and conducting simulations.

Simulate the usage case with `simulate.py`: `python scripts/simulate.py -inp <cases_file_path>`.

- Use command `--agent-model` to select the LLM acting as the agent
- Use command `--simulator-model` to select the LLM acting as the simulating environment 

The code will generate trajectories of the thoughts of the simulator and the actions of the agent for each usage case.

### Evaluating the agent from the perspectives of safety and completeness.

Assess the trajectories with `evaluate.py`: `python scripts/evaluate.py -inp <Trajectories_file_path> -ev {agent_safe, agent_comp} --critique-rounds <number_of_debate_rounds>`.

- Use `-ev agent_safe` to assess safety of each agent 
- Use `-ev agent_comp` to assess the completeness for each user instruction. 
- `--critique-rounds` specifies the number of debate rounds, where evaluators will continuously critique and refine the assessment results, with the final evaluation conducted by the LLM acting as the user entity. The more rounds you set, the longer the prompt will be. 

Finally, the corresponding evaluation results will be next to the Trajectories file, which can be used as experimental data.