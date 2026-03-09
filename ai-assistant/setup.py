#Used when installing project as a Python package.

from setuptools import setup, find_packages

setup(
    name="generative-ai-project",   
    version="0.1.0",
    author="Akshara R",
    author_email="akshararamesh0512@gmail.com",

    package_dir={"": "src"},
    packages=find_packages(where="src"),

    install_requires=[],
)
