import setuptools

setuptools.setup(
    name="tatomecab",
    version="0.1",
    author="Gilles Bedel",
    author_email="gillux@tatoeba.org",
    description="A wrapper around Mecab for the Tatoeba project",
    url="https://github.com/Tatoeba/tatomecab",
    packages=['tatomecab'],
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
    scripts=['scripts/tatomecab', 'scripts/tatomecab-webserver']
)
