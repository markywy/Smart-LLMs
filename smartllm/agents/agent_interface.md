## Our interface
We design an agent interface that is compatible with our [app specification](../../assets/README.md#app-specification).

The interface is implemented in [`zero_shot_agent_with_app`](zero_shot_agent_with_app.py). The key difference made here is simply that we implemented a `ZeroShotAgentWithApp` class that subclasses the `ZeroShotAgent` class and accepts our apps instead of apps as inputs.

## Virtual agent executor
For our purpose, we use two different Language Models:
- **Agent**: utilizes provided apps to help with user's instruction.
- **Emulator**: emulates the app output based on the agent's action and the app specification.

The agent provides app actions (`Action`) and inputs (`Action input`). The emulator LM emulates the app execution and returns the virtual outputs (`Observation`) to the agent for next actions.

The implementation is in [`agent_executor.py`](agent_executor.py). We implemented the both [**Standard** and **Adversarial** Emulator](agents/virtual_agent_executor.py) that emulating the results with an LM instead of actually executing the apps. 
