from setuptools import find_packages, setup

from stats import __version__

setup(
    name="stats",
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
    entry_points={"console_scripts": ["stats=stats.__main__:main"]},
)
