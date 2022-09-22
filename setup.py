from os import getenv

from setuptools import setup

def get_required_packages():
    result = []
    with open("requirements.txt") as f:
        result += list(f.read().splitlines())
    return result


setup(
    name="python_azure",
    version="0.0.1",
    packages=[""],
    package_dir={"": "src"},
    author="Nipun Bahri",
    author_email="bahri.nipun@gmail.com",
    python_requires=">=3.7",
    description="This library is Python Azure Integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
setup(
    version=getenv("TEST_VERSION")
)
