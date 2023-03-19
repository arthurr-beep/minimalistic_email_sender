from setuptools import setup, find_packages

setup(
    name="minimalistic-email-sender",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "smtplib",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    author="Arthur A",
    author_email="arthurraugustus@gmail.com",
    description="A Python package to send emails using SMTP providers.",
)
