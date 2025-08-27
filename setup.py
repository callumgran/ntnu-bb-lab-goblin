from setuptools import setup, find_packages

setup(
    name="ntnu-bb-downloader-cli",
    version="0.1.0",
    author="Callum Gran",
    author_email="callum.gran@gmail.com",
    description="A command-line tool for downloading submissions from NTNU Blackboard.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bb-downloader-cli",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "selenium",
        "webdriver-manager",
        "argparse",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)