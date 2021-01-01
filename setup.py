#!/usr/bin/env python

from setuptools import setup

requirements = ["Django", "requests"]  # add Python dependencies here
# e.g., requirements = ["PyYAML"]

setup(
    name='cyberark-aim-ccp-lookup-awsaccesskeyid',
    version='0.1',
    author='Craig Geneske, CyberArk',
    author_email='craig.geneske@cyberark.com',
    description='Retrieves AWS Access Key ID (instead of password) from a CyberArk vaulted object',
    long_description='',
    license='Apache License 2.0',
    keywords='ansible',
    url='http://github.com/cgeneske/cyberark-aim-ccp-lookup-awsaccesskeyid',
    packages=['cyberark-aim-ccp-lookup-awsaccesskeyid'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=requirements,
    entry_points = {
        'awx.credential_plugins': [
            'aim_plugin = cyberark-aim-ccp-lookup-awsaccesskeyid:aim_plugin'
        ]
    }
)
