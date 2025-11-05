"""
Setup script for Policy-to-Code Pipeline
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="policy-to-code",
    version="1.0.0",
    description="Transform plain text policies into executable Python functions with AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Policy-to-Code Team",
    author_email="",
    url="https://github.com/yourusername/agentic-rules-to-code",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        # Core has no dependencies!
    ],
    extras_require={
        "ai": [
            "openai>=1.0.0",
            "python-dotenv>=1.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "policy-to-code=pipeline:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="policy automation code-generation ai azure-openai travel-policy rules-engine",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/agentic-rules-to-code/issues",
        "Source": "https://github.com/yourusername/agentic-rules-to-code",
        "Documentation": "https://github.com/yourusername/agentic-rules-to-code/blob/main/docs/",
    },
)
