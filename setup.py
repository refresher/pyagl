import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyagl",
    version="0.0.1",
    author="Edi Feschiyan",
    author_email="edi.feschiyan@konsulko.com",
    description="Python bindings and tests for Automotive Grade Linux services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/refresher/pyagl",
    packages=setuptools.find_packages(),
    license="Apache 2.0",
    install_requires=['websockets', 'parse', 'asyncssh', 'pytest', 'pytest-asyncio'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)
