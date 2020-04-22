from setuptools import setup, find_packages

# TODO: Add proper metadata
setup(
    name="multiplex",
    version="0.1",
    packages=find_packages(),
    install_requires=[
       'configurator>=1.3'
    ]
)
