from pathlib import Path

from setuptools import find_packages
from setuptools import setup

about = {}
with open(Path(__file__).parent / "bro" / "__version__.py", "r") as f:
    exec(f.read(), about)

long_description = (Path(__file__).parent / "README.md").read_text()
long_description = long_description.replace("X.Y.Z", about["__version__"])

setup(
    name="bro",
    version=about["__version__"],
    description="Open source python library for accessing BRO API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VIKTOR",
    author_email="support@viktor.ai",
    license="see LICENSE.txt",
    license_files=("LICENSE.txt",),
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "xmltodict>=0.13.0",
        "requests>=2.31.0",
        "lxml>=5.1.0",
        "pyproj>=3.6.1",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    test_suite="tests",
    project_urls={
        "Source code": "https://github.com/viktor-platform/bro",
        "Example VIKTOR application": "https://demo.viktor.ai/public/bro-app",
        "Source code VIKTOR application": "https://github.com/viktor-platform/bro-app",
    },
)
