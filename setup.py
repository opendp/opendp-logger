from setuptools import find_packages, setup

setup(
    name="opendp-logger",
    version="0.3.0",
    description="A logger wrapper for OpenDP to keep track of, import, export the AST",
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    url="https://github.com/opendp/opendp-logger",
    author='The OpenDP Project',
    author_email='info@opendp.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ], 
    keywords='opendp logger ast',
    packages=find_packages(),
    python_requires=">=3.8, <4",
    install_requires=[
        "opendp >= 0.8.0"
    ],
)