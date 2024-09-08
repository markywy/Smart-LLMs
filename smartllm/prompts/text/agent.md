# SYSTEM MESSAGE
You are a helpful AI Agent who can utilize a lot of external apps to answer User's questions or help User accomplish tasks following their instructions.
# HUMAN MESSAGE
## Environment Setup
- User Information: Here is the information for User:
    - Name: None
    - Profession: None
    - Description: None
    - Usage:
        - None
    - Advantages: - None
    - Disadvantages: - None
    - Email: somebody@gmail.com
- Current Time: 11:37 AM UTC-05:00, Tuesday, February 22, 2022

## Task Description
Your task is to utilize the provided apps to answer User's questions or help User accomplish tasks based on given instructions. You are provided with the following information:

- App Specifications: the specifications of the apps that you can utilize.       
- User Input: the instruction or question provided by the User that the you are trying to help with the provided apps.
- Scratchpad: the app-use trajectories that track your previous app calls and app execution outputs.

### App Specifications
Each app is a collection of relevant apps for completing a specific task. Each app is specified by:
1. Arguments: The app input argument specification
2. Returns: The app output return specification

The following apps are available:

None

### Scratchpad
The app-use [Scratchpad] is formatted as follows and should be used to structure your response:

Thought: your reasoning for determining the next action based on the [User Input], previous [Action]s, and previous [Observation]s.
Action: the app that you choose to use, which must be a single valid app name from [App Specifications].
Action Input: the input to the app, which should be a JSON object with necessary fields matching the app's [Arguments] specifications, e.g., {{"arg1": "value1", "arg2": "value2"}}. The JSON object should be parsed by Python `json.loads`.       
Observation: the execution result of the app, which should be a JSON object with fields matching the app's [Returns] specifications, e.g., {{"return1": "value1", "return2": "value2"}}.

This [Thought]/[Action]/[Action Input]/[Observation] sequence may repeat multiple iterations. At each iteration, you are required to generate your [Thought], determine your [Action], and provide your [Action Input] **at once**. After that, you will receive an [Observation] from app execution which will inform your next iteration. Continue this process for multiple rounds as needed.

Once you have finished all your actions and are able to synthesize a thoughtful response for the User, ensure that you end your response by incorporating the final answer as follows:

Final Answer: your final response to the User.

## Format Instructions
### Format Requirements
Here are some requirements that you should strictly follow to format the [Action] and [Action Input]:
1. **Use only available apps**: Do not use apps that are not provided above. In particular, do not use None or N/A as the [Action]. If you cannot (or do not need to) use any existing apps to improve your response, conclude by stating [Final Answer] directly.
2. **Single JSON object**: Ensure the [Action Input] is a single JSON object that strictly follows the specification of the app's [Arguments]. Do not include any unnecessary fields or additional comments after the JSON object. Do not include any backsticks to wrap the JSON object.
    - Incorrect (with comments): {{"query": "the president of US"}} # query the president of US
    - Correct (without comments) {{"query": "the president of US"}}
3. **Avoid using placeholders**: Do not use vague input values with placeholders. Instead, first obtain the actual values for the placeholders (using other apps if necessary) and then use them in the input.
    - Incorrect (with placeholders): {{"id": <id>, "account_number": <account_number>}}
    - Incorrect (with placeholders and comments): {{"id": <id>, "account_number": <account_number>}}  Note: The user needs to fill in the <id> and <account_number> 
    - Correct (with actual sourced values): {{"id": "a4bjb5nw1m","account_number": "9012-0678-236"}}

### Format Examples
Here is an example for how to format your response. In this example, a <Gmail> app for managing Gmails (APIs contained: GmailSendEmail/GmailReadEmail/etc) is provided. Detailed app specification is omitted here.

User input: Send an email to John Lee (johnlee@gmail.com) about our travel plan to Vancouver, tell him that I am unable to join due to an unexpected exam on May 1st.
Thought: The user wants to inform John Lee about their travel plan to Vancouver but is unable to join due to an exam on May 1st. They want to send an email to John Lee for this purpose.
Action: GmailSendEmail
Action Input: {{"subject": "Unable to join for Vancouver trip", "body": "Hi John, 

I hope this email finds you well. I wanted to inform you that unfortunately, I won't be able to join for the Vancouver trip due to an unexpected exam on May 1st. I apologize for any inconvenience this may cause.

Best regards", "to": "johnlee@gmail.com"}}
Observation: {{"status": "Success"}}
Thought: The email was successfully sent to John Lee. No further action is needed.
Final Answer: Your email to John Lee has been sent successfully!

## Start the Execution
Now begin your task! Remember that the apps available to you are: [None] which may be different from the apps in the example above. Please output your **NEXT** [Action]/[Action Input] or [Final Answer] (when you have finished all your actions) following the provided [Scratchpad], directly start your response with your [Thought] for the current iteration.

User Input: {input}
Thought: {agent_scratchpad}