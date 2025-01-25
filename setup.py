import io

import setuptools


ABOUT_INFO = {}
with open("./doubo/__about__.py") as f:
    exec(f.read(), ABOUT_INFO)


try:
    with io.open("README.md", encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = ""


REQUIRES = []
with open("requirements.txt") as f:
    for line in f:
        line, _, _ = line.partition("#")
        line = line.strip()
        REQUIRES.append(line)


setuptools.setup(
    name=ABOUT_INFO['__package_name__'],
    version=ABOUT_INFO['__version__'],
    license=ABOUT_INFO['__license__'],
    description=ABOUT_INFO['__description__'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author_email=ABOUT_INFO['__author_email__'],
    author=ABOUT_INFO['__author__'],
    install_requires=REQUIRES,
    python_requires=">=3.8",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points = """
        [console_scripts]
        doubo = doubo.cli:app
    """,
)
