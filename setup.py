# -----------------------------------------------------------------------------
# (C) 2023 Higor Grigorio (higorgrigorio@gmail.com)  (MIT License)
# -----------------------------------------------------------------------------

# coding: utf-8

import setuptools
import os

with open('./README.md', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="olympus",
    version="0.1.0",
    author="Higor Grigorio",
    author_email="higorgrigorio@gmail.com",
    description="A library for functional programming in Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HigorGrigorio/olympus.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.9',
)
