from setuptools import setup, find_packages
from stats import __version__

setup(
    name="app",
    version=__version__,
    packages=find_packages(),
    install_requires=[

    ],
    entry_points={
        'console_scripts': [
            'stats=stats'
        ]
    },
)
