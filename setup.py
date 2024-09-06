import setuptools

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="smartllm",
    version="0.1.0",
    author="Mark Ye, Jerry Li, Jack Zhang",
    description="A Simulated Multi-Agent Risk and Task Assessment for LLMs",
    url="https://github.com/markywy/SmartLLMs",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    python_requires=">=3.6",
)
