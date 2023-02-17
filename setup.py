from setuptools import setup, find_packages
from pathlib import Path

about = {}
with open(Path(__file__).parent / 'bro' / '__version__.py', 'r') as f:
    exec(f.read(), about)

setup(
    name='bro-api',
    version=about['__version__'],
    description='Open source python library for accessing BRO API',
    long_description='this is a long description',
    long_description_content_type="text/markdown",
    url='https://github.com/viktor-platform/bro-api',
    author='VIKTOR',
    author_email='support@viktor.ai',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=[
    ],
    test_suite='tests',
)
