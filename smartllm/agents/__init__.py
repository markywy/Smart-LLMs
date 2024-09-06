from .agent_executor import AgentExecutorWithApp
from .virtual_agent_executor import (
    AdversarialVirtualAgentExecutorWithApp,
    StandardVirtualAgentExecutorWithApp,
)
from .virtual_agent_executor_zh import (
    AdversarialVirtualAgentExecutorWithAppZh,
    StandardVirtualAgentExecutorWithAppZh,
)
from .zero_shot_agent_with_application import AGENT_TYPES, ZeroShotAgentWithApp
from .zero_shot_agent_with_application_zh import AGENT_TYPES, ZeroShotAgentWithAppZh

SIMULATORS = {
    "normal": AgentExecutorWithApp,
    "std_thought": StandardVirtualAgentExecutorWithApp,
    "adv_thought": AdversarialVirtualAgentExecutorWithApp,
}
SIMULATORS_ZH = {
    "normal": AgentExecutorWithApp,
    "std_thought": StandardVirtualAgentExecutorWithAppZh,
    "adv_thought": AdversarialVirtualAgentExecutorWithAppZh,
}
