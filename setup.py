from setuptools import find_packages, setup

from ecst import __version__

setup(
    name="ecst",
    version=__version__,
    packages=find_packages(),
    install_requires=["aiohttp", "pydantic>=2.0.0", "sqlalchemy[asyncio]", "aiosqlite"],
    extras_require={
        "dev": [
            "setuptools>65.5.0",
            "flake8",
            "pydocstyle",
            "piprot",
            "pytest",
            "pytest-cov",
            "pytest-asyncio",
            "isort",
            "black",
            "safety",
            "aioresponses",
        ],
    },
    entry_points={"console_scripts": ["ecst=ecst.__main__:main"]},
)
