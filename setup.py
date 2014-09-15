# Copyright (C) 2014 InfiniDB, Inc.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2 of
# the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA. 

from setuptools import setup, find_packages

import os
from glob import glob

playbook_template = {}

for root, dirs, files in os.walk('playbook_template'):
    for filename in files:
        filepath = os.path.join(root, filename)

        if root not in playbook_template:
            playbook_template[root] = []

        playbook_template[root].append(filepath)

share = {}
for root, dirs, files in os.walk('share'):
    for filename in files:
        filepath = os.path.join(root, filename)

        if root not in share:
            share[root] = []

        share[root].append(filepath)

examples = [ ('examples', glob('examples/*')) ]
conf = [ ('conf', glob('conf/*')) ]

VERSION = '1.0.0'
DESCRIPTION = 'InfiniDB Enterprise Manager Tools'
LONG_DESCRIPTION = open('README.md').read()

setup(
    name='infinidb-em-tools',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='InfiniDB, Inc.',
    author_email='info@infinidb.co',
    url='https://bitbucket.org/infinidb/infinidb-em-tools',
    license="GPL License",
    platforms=["any"],
    packages=find_packages(),
    package_data={'emtools': ['config.json']},
    scripts=glob('bin/*'),
    data_files=playbook_template.items() + share.items() + examples + conf,
    install_requires=["validictory >= 0.9"]
)

