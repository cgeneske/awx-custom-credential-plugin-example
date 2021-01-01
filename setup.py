#!/usr/bin/env python

from setuptools import setup

requirements = ["Django", "requests"]  # add Python dependencies here
# e.g., requirements = ["PyYAML"]

setup(
    name='cyberark-aim-ccp-lookup-username',
    version='0.1',
    author='Craig Geneske, CyberArk',
    author_email='craig.geneske@cyberark.com',
    description='Retrieves username (instead of password) from a CyberArk vaulted object',
    long_description='',
    license='Apache License 2.0',
    keywords='ansible',
    url='http://github.com/cgeneske/cyberark-aim-ccp-lookup-username',
    packages=['cyberark-aim-ccp-lookup-username'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[],
    install_requires=requirements,
    entry_points = {
        'awx.credential_plugins': [
            'aim_plugin = cyberark-aim-ccp-lookup-username:aim_plugin',
        ]
    }
)
