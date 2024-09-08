import setuptools

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="smartllm",
    version="0.1.0",
    author="Mark Ye, Jerry Li, Jack Zhang",
    description=" Multi-Agent and Multilingual Framework for Personalized Risk Simulation and Assessment in Large Language Model Applications",
    url="https://github.com/markywy/SmartLLMs",
    packages=setuptools.find_packages(),
    install_requires=[
        requirements,
        "@git+https://github.com/dhh1995/PromptCoder.git#egg=package_name"
    ],
    python_requires=">=3.6",
)
