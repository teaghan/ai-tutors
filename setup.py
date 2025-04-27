from setuptools import setup

setup(
    name="ai_tutors",
    version="1.0.0",
    packages=["ai_tutors"],
    install_requires=[
        "requests",
        "pandas",
        "ipython",
    ],
    author="Teaghan O'Briain",
    author_email="obriaintb@gmail.com",
    description="A library for interacting with AI Tutors",
    long_description=open("ai_tutors/README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/teaghan/ai-tutors",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.8",
) 