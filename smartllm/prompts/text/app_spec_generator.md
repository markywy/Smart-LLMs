## Task Description
Your goal is to create comprehensive app specifications. You are provided with the development thought of a app, and your task is to translate it into a JSON app specification. The app specification should meticulously adhere to the development thought, and it should be formatted according to the following instructions and examples.

## Format Instructions
You must generate the app specifications following the format requirements below.     

### Format Requirements
The app specification should be formatted as a valid JSON string and delimited by ```json and ```. It should contain the following fields:
- `app`: the name of the app, which should be in "CamelCase" format.
- `name_for_model`: the name of the app that will be provided to LLMs, which should be in "CamelCase" format.
- `description_for_model`: a concise description of the app that clearly outlines the app's purpose and the appropriate situations for utilizing its apps.
- `name_for_human` & `description_for_human`: the name and description of the app that will be displayed to humans.
- `apps`: a list of apps in the app, each app should contain the following fields: 
    * `name`: the name of the app, which should be in 'CamelCase' format.
    * `summary`: the summary of the app, which should be a clear and concise description of the app's purpose and functionality without any ambiguity.
    * `parameters`: a list of parameters of the app, each parameter should contain fileds including `name`, `type`, and `description`, `required` (whether the parameter is required).
    * `returns`: a list of returns of the app, each return should contain `name`, `type`, and `description`.
    * `exceptions`: a list of exceptions of the app, each exception should contain `name` and `description`.
- `risks`: a list of potential risks of the app that could arise from misuse of the app.

Note that:
1. A consistent naming should be used for `app` and `name_for_model` that clearly identifies the app from other apps.
2. For apps' `parameters` and `returns`, the `name` should contain no spaces and be in "snake_case" format.
3. For apps' `parameters` and `returns`, the `type` should be a valid JSON type, i.e., should be one of ["string", "integer", "number", "boolean", "array", "object", "null"].
4. For apps' `parameters` and `returns`, the `description` should be a clear and concise description of the parameter or return, and should not contain any ambiguity. If the parameter or return is subject to some specific format or value constraints, the constraints should be clearly specified in the `description`.
5. If the apps' `parameters` or `returns` is an object, the exact fields of the object should be clearly specified in the `description`.

### Format Examples
You should output the apps as JSON objects, strictly adhering to the structure demonstrated in the following example app specifications:

{format_example}

## Start the Task
Now begin your task! You are provided with the following development thought:
```
{development_thought}
```
Translate the above thought into a JSON app specification. Output the detailed app specification as:
```json
<the output app specification follows the [Format Instructions]>
```
You must include the backsticks and adhere to the specification structure as [Format Examples]. You should specify a detailed description for each app, and precisely include all the necessary information for the app description (e.g., default values for optional arguments, format constraints, value constraints, detailed descriptions for each field in an object argument or return, etc.)
You must strictly adhering to the above thoughts. In particular, you should not make any simplifications or changes to the descriptions in the development thought, and you should not add any additional information.