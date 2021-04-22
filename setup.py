import sys
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    INSTALL_REQUIRES = [x.strip() for x in f.readlines()]

with open('requirements-dev.txt') as f:
    TEST_REQUIRES = [x.strip() for x in f.readlines()]

if sys.version_info < (3, ):
    TEST_REQUIRES += ['mock']

with open('README.rst') as f:
    readme = f.read()

setup(
    name="iec870ree",
    version="0.7.0",
    author="GISCE-TI, S.L.",
    author_email="devel@gisce.net",
    description=("Library to connect and query information about electric"
                 "meters following REE protocol."),
    long_description=readme,
    long_description_content_type="text/x-rst",
    url="https://github.com/gisce/iec870ree",
    license="GNU Affero General Public License v3",
    install_requires=INSTALL_REQUIRES,
    setup_requires=["pytest-runner"],
    tests_require=TEST_REQUIRES,
    packages=find_packages(exclude=('tests', 'docs', 'examples')),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities"
    ],
)
