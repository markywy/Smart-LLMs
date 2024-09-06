# Assets for Generation
This folder contains assets for generating test cases and apps, see [generation scripts](../../scripts/generation/README.md) for more details.

## Test case generation
To generate a test case, the [script](../../scripts/generation/generate_test_cases.py) need to take both app specification and a list of potential risks. For our curated apps, they are provided in `../all_apps.json` and `app_risk.json`.

We use examples to guide the generation process, which can be chosen from
* `format_example_cases.json`: A list of human-written test cases.
* `format_example_case_zero.json`: A dummy test cases only contains format information.

## App generation
To generate a app in a specific category, we
* generate a list of app names using the [script](../../scripts/generation/generate_tool_names.py) with `tool_taxonomy.json`.
* generate the app using the [script](../../scripts/generation/generate_tool_thoughts.py) with `format_example_tool.json` and the generated app names.