from setuptools import find_packages, setup

from stats import __version__

setup(
    name="stats",
    version=__version__,
    packages=find_packages(),
    install_requires=["aiohttp", "motor", "pydantic>=2.0.0", "montydb[lmdb]", "sqlalchemy[asyncio]"],
    extras_require={
        "dev": [
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
    entry_points={"console_scripts": ["stats=stats"]},
)
