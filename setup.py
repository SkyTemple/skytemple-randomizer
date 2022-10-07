__version__ = '1.4.0.post0'
from setuptools import setup, find_packages

# README read-in
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
# END README read-in

install_requires = [
    'ndspy >= 3.0.0',
    'skytemple-files[spritecollab] >= 1.4.0',
    'explorerscript >= 0.1.0',
    'skytemple-icons >= 1.3.2',
    'pygobject >= 3.26.0',
    'strictyaml >= 1.6.0',
    'jsonschema >= 4.1.2',
    'packaging'
]
package_data = ['frontend/gtk/*.glade', 'frontend/gtk/*.css', 'data/*/*/*/*/*', 'data/*', 'data/*/*', 'py.typed']

if __name__ == '__main__':
    setup(
        name='skytemple-randomizer',
        version=__version__,
        packages=find_packages(),
        description='Randomizer GUI to randomize the ROM of Pokémon Mystery Dungeon Explorers of Sky (EU/US)',
        long_description=long_description,
        long_description_content_type='text/x-rst',
        url='https://github.com/SkyTemple/skytemple-randomizer/',
        install_requires=install_requires,
        extras_require={
            'web': [
                'tornado >= 6.1'
            ],
        },
        classifiers=[
            'Development Status :: 4 - Beta',
            'Programming Language :: Python',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
        ],
        package_data={'skytemple_randomizer': package_data},
        entry_points='''
            [console_scripts]
            skytemple_randomizer=skytemple_randomizer.frontend.gtk.main:main
        ''',
    )
