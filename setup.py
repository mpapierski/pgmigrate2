#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='pgmigrate2',
      
    packages=find_packages(),
    version='1.2.0',
    description='Database schema migration tool for people who do not afraid SQL',
    author='Sergey Kirillov',
    author_email='sergey.kirillov@gmail.com',
    url='https://bitbucket.org/shopium/pgmigrate2',
    install_requires=['sqlalchemy'],
    license="Apache License 2.0",
    keywords="database migration tool postgres postgresql mysql sqlite",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
#                       "License :: OSI Approved :: BSD License",
 #                      "Topic :: Software Development :: Libraries :: Python Modules",
                       "Operating System :: OS Independent",
                       "Natural Language :: English",
                   ],


    zip_safe=False,
      
    entry_points = {
        'console_scripts': [
            'pgmigrate2 = pgmigrate2.main:main',
        ],
    },
      
    long_description=open('README.rst').read().decode('utf-8')    
)
