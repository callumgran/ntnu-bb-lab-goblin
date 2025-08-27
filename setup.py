from setuptools import setup, find_packages
from pathlib import Path

README = Path(__file__).with_name("README.md")
long_desc = README.read_text(encoding="utf-8") if README.exists() else ""

setup(
    name="ntnu-bb-lab-goblin",
    version="0.1.0",
    author="Callum Gran",
    author_email="callum.gran@gmail.com",
    description="A CLI goblin that crawls NTNU Blackboard and downloads + renames student submissions.",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/callumgran/ntnu-bb-lab-goblin",
    project_urls={
        "Homepage": "https://github.com/callumgran/ntnu-bb-lab-goblin",
        "Repository": "https://github.com/callumgran/ntnu-bb-lab-goblin",
        "Issues": "https://github.com/callumgran/ntnu-bb-lab-goblin/issues",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    py_modules=["cli"],
    include_package_data=True,
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=4.0.0",
        "tqdm>=4.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "bb-downloader=cli:main",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Utilities",
    ],
)
