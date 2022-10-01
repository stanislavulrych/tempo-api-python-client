import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tempo-api-python-client",
    version="0.6.0",
    author="Stanislav Ulrych",
    author_email="stanislav.ulrych@gmail.com",
    description="Python bindings for Tempo (https://apidocs.tempo.io/)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stanislavulrych/tempo-api-python-client",
    packages=setuptools.find_packages(exclude=('tests',)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests",
        "six"
    ],
    python_requires='>=3.6.9',
)
