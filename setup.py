__version__ = '1.0.6'
from setuptools import setup, find_packages

# README read-in
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# END README read-in


setup(
    name='skytemple-randomizer',
    version=__version__,
    packages=find_packages(),
    description='Randomizer GUI to randomize the ROM of Pokémon Mystery Dungeon Explorers of Sky (EU/US)',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    url='https://github.com/SkyTemple/skytemple-randomizer/',
    install_requires=[
        'ndspy >= 3.0.0',
        'skytemple-files >= 1.1.3',
        'explorerscript >= 0.0.7',
        'skytemple-icons >= 0.1.0',
        'pygobject >= 3.26.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    package_data={'skytemple_randomizer': ['*.glade', 'data/*/*/*/*/*', 'data/*', 'data/*/*']},
    entry_points='''
        [console_scripts]
        skytemple_randomizer=skytemple_randomizer.main:main
    ''',
)
