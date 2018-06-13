# setup.py for clautod package
# Relies on clautod-version.txt being populated, which should be done by the clautod-package.sh script

import setuptools
import re

# Pull description from README
with open("README.md", "r") as fh:
    long_description = fh.read()

# Pull version from version file, populated before
with open("clautod-version.txt", "r") as fh:
    lines = fh.readlines()

# Filter out comments and whitespace
lines = [line.strip() for line in lines]
lines = [line for line in lines if not line == ""]
lines = [line for line in lines if not line.startswith('#')]

# Sanity checks
if not len(lines) == 1:
    print("clautod-version contents invalid")
    exit(1)
if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+\-[0-9][0-9][0-9][0-9]$", lines[0]):
    print("Invalid version <" + lines[0] + ">")
    exit(1)
clautod_version = lines[0]

setuptools.setup(
    name="clautod",
    version=clautod_version,
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
