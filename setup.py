import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tempo-api-python-client",
    version="0.2.0",
    author="Stanislav Ulrych",
    author_email="stanislav.ulrych@gmail.com",
    description="Python bindings for Tempo (https://tempo-io.github.io/tempo-api-docs/)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stanislavulrych/tempo-api-python-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
