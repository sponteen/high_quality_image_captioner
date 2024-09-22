#!/usr/bin/env python

"""The setup script."""

# export DISTUTILS_DEBUG=True

from setuptools import setup, find_packages

with open("README.md") as readme_file:
    readme = readme_file.read()


with open("HISTORY.md") as history_file:
    history = history_file.read()


with open("requirements/base.txt") as requirements_file:
    requirements = requirements_file.readlines()

with open("requirements/testing.txt") as dev_requirements_file:
    dev_requirements = dev_requirements_file.readlines()
    dev_requirements.extend(requirements)

setup(
    author="Vladimir Rotariu",
    author_email="rotariuvladimir@gmail.com",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
    ],
    description="High Quality Image Captioner",
    entry_points={
        "console_scripts": [
            "aiml=aiml.cli.main:main",
        ],
    },
    install_requires=requirements,
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="aiml",
    name="aiml",
    packages=find_packages(include=["aiml", "aiml.*"]),
    test_suite="tests",
    tests_require=dev_requirements,
    url="https://github.com/sponteen/high_quality_image_captioner",
    version="0.1.0",
    zip_safe=False,
)
