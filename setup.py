from setuptools import setup, find_packages

with open('LICENSE') as f:
    license = f.read()

with open('README.rst') as f:
    readme = f.read()

setup(
    name="reeprotocol",
    version="0.0.dev0",
    author="Javier de la Puente",
    author_email="jdelapuentealonso@gmail.com",
    description=("Library to connect and query information about electric"
                 "meters following REE (Red Eléctrica Española) protocol."),
    license=license,
    keywords="REE electric meters IEC 870-5-102",
    url="http://www.javierdelapuente.com",
    packages=find_packages(exclude=('tests', 'docs')),
    long_description=readme,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Topic :: Communications :: FIDO :: IEC 870-5-102",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
)
