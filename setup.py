from setuptools import setup, find_packages

setup(
    name="code-review-assistant",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.111.0",
        "uvicorn[standard]==0.30.1",
        "pydantic==2.7.4",
        "pydantic-settings==2.3.3",
        "sqlalchemy==2.0.30",
        "psycopg2-binary==2.9.9",
        "python-multipart==0.0.9",
        "pytest==8.2.2",
        "httpx==0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "code-review=src.main_cli:main",
        ],
    },
    python_requires=">=3.11",
)
