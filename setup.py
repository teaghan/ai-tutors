from setuptools import setup
import os

# Read the README content from the file, handling potential errors
readme_path = os.path.join('ai_tutors', 'README.md')
try:
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "AI Tutors - A library for interacting with AI Tutors through a REST API."

setup(
    name="ai_tutors",
    version="1.0.1",
    packages=["ai_tutors"],
    install_requires=[
        "requests",
        "pandas",
        "ipython",
    ],
    author="Teaghan O'Briain",
    author_email="obriaintb@gmail.com",
    description="A library for interacting with AI Tutors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/teaghan/ai-tutors",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
) 