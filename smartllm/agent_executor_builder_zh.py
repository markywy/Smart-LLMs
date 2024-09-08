from langchain.base_language import BaseLanguageModel
from langchain.callbacks.base import BaseCallbackManager
from langchain.chat_models.base import BaseChatModel
from smartllm.agents import (
    SIMULATORS_ZH,
    AgentExecutorWithApp,
    ZeroShotAgentWithAppZh,
)
from smartllm.apps import get_applications_by_names
from smartllm.utils.my_typing import *


def build_agent_executor(
    user, 
    applications: List[str],
    agent_llm: BaseLanguageModel,
    simulator_llm: BaseLanguageModel,
    critiquer_llm: Optional[BaseLanguageModel] = None,
    num_critique_steps: int = 0,
    max_allowed_steps: int = 3,
    agent_type: str = "naive",
    simulator_type: str = "std_thought",
    verbose: bool = True,
    return_intermediate_steps: bool = True,
    max_iterations: int = 15,
    callback_manager: Optional[BaseCallbackManager] = None,
) -> Type[AgentExecutorWithApp]:
    applications = get_applications_by_names(applications)
    agent = ZeroShotAgentWithAppZh.from_llm_and_apps(
        user=user, 
        applications=applications,
        llm=agent_llm,
        agent_type=agent_type,
        use_chat_format=isinstance(agent_llm, BaseChatModel),
    )
    executor_class = SIMULATORS_ZH[simulator_type]
    if simulator_type != "normal":
        agent_executer = executor_class.from_agent_and_apps(
            user=user, 
            applications=applications,
            agent=agent,
            verbose=verbose,
            llm_simulator=simulator_llm,
            llm_critiquer=critiquer_llm,
            num_critique_steps=num_critique_steps,
            max_allowed_steps=max_allowed_steps,
            use_chat_format=isinstance(simulator_llm, BaseChatModel),
            return_intermediate_steps=return_intermediate_steps,
            max_iterations=max_iterations,
            callback_manager=callback_manager,
        )
    else:
        agent_executer = executor_class.from_agent_and_apps(
            user=user, 
            applications=applications,
            agent=agent,
            verbose=verbose,
            max_iterations=max_iterations,
            callback_manager=callback_manager,
        )
    return agent_executer
