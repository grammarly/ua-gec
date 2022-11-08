from setuptools import setup, find_packages
from codecs import open
from os import path

VERSION = "2.0.0.dev0"
here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="ua_gec",
    # Versions should comply with PEP440. For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION,
    author="Oleksiy Syvokon",
    author_email="oleksiy.syvokon@gmail.com",
    description="UA-GEC: Grammatical Error Correction and Fluency Corpus for the Ukrainian language",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/grammarly/ua-gec",
    license="License :: OSI Approved :: CC-BY-4.0",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Natural Language :: Ukrainian",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="gec ukrainian dataset corpus grammatical error correction grammarly",
    packages=find_packages(exclude=["docs", "tests"]),
    package_data={
        "ua_gec": [
            "data/*",
            "data/gec-fluency/train/annotated/*",
            "data/gec-fluency/test/annotated/*",
            "data/gec-only/train/annotated/*",
            "data/gec-only/test/annotated/*",
        ]
    },
    # include_package_data=True,
    install_requires=[
    ],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={"test": ["pytest", "coverage"]},
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={"console_scripts": []},
    python_requires='>=3.6',
)
