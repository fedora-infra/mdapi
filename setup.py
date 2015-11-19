#!/usr/bin/env python3

"""
Setup script
"""


from setuptools import setup


def get_requirements(requirements_file='requirements.txt'):
    """Get the contents of a file listing the requirements.

    :arg requirements_file: path to a requirements file
    :type requirements_file: string
    :returns: the list of requirements, or an empty list if
              `requirements_file` could not be opened or read
    :return type: list
    """

    lines = open(requirements_file).readlines()
    return [
        line.rstrip().split('#')[0]
        for line in lines
        if not line.startswith('#')
    ]

print(get_requirements())

setup(
    name='mdapi',
    description='A simple API to serve the package repository metadata',
    version='2.1',
    author='Pierre-Yves Chibon',
    author_email='pingou@pingoured.fr',
    maintainer='Pierre-Yves Chibon',
    maintainer_email='pingou@pingoured.fr',
    license='GPLv2+',
    download_url='https://pagure.io/releases/mdapi',
    url='https://pagure.io/mdapi',
    packages=['mdapi'],
    include_package_data=True,
    install_requires=get_requirements(),
    scripts=['mdapi-get_repo_md', 'mdapi-run'],
)
