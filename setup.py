import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clautod",
    version="0.0.1-0001",
    author="Jeremy Lerner",
    author_email="jeremy.cpsc.questions@gmail.com",
    description="Consumables-Listing AUTOmation Daemon",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeremy-quicklearner/clautod",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
