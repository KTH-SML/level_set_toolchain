import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylevel",
    version="1.0.0",
    author="Frank Jiang, Philipp Rothenhäusler",
    author_email="fjiang@kth.se, philipp.rothenhaeusler@gmail.com",
    description="Python package for MATLAB based Levelset toolbox.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KTH-SML/SML_level_set.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
