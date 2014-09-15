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

'''
emtools.cluster.pkgfilenameparser

Utility used to parse a package file name.
'''
import os
import re
import emtools.common as common
import emtools.common.utils as utils

#TODO: Consider changing autooam to use this class to avoid duplicate code

class PkgFileNameParser(object):
    def __init__(self):
        '''
        Constructor.
        
        Carries regular expression dictionary with package tarball file names.
        Can be used to extract specific parts of the tar ball file name.
        '''
        self._filepatt = {
            'binary' : re.compile('(calpont-|)infinidb-ent-([0-9\-\.]*).x86_64.bin.tar.gz'),
            'deb' : re.compile('(calpont-|)infinidb-ent-([0-9\-\.]*).amd64.deb.tar.gz'),
            'rpm' : re.compile('(calpont-|)infinidb-ent-([0-9\-\.]*).x86_64.rpm.tar.gz'),
            'binary-datdup' : re.compile('calpont-infinidb-datdup-(.*).x86_64.bin.tar.gz'),
            # debian support is via the binary package for now
            'deb-datdup' : re.compile('calpont-infinidb-datdup-(.*).x86_64.bin.tar.gz'),
            'rpm-datdup' : re.compile('calpont-datdup-(.*).x86_64.rpm'),
            'binary-std' : re.compile('infinidb-([0-9\-\.]*).x86_64.bin.tar.gz'),
            'deb-std' : re.compile('infinidb-([0-9\-\.]*).amd64.deb.tar.gz'),
            'rpm-std' : re.compile('infinidb-([0-9\-\.]*).x86_64.rpm.tar.gz'),
        }
        self._verspatt = re.compile('(calpont-|)infinidb-(ent-|)(.*).(x86_64.bin|amd64.deb|x86_64.rpm).tar.gz')

    def get_pkg_version(self, pfile):
        '''
        Extracts the version number out of a package tarball name.
        
        @param pfile - relative path to a package tarball file
        
        @return      - the version number component that is embedded in 
                       that filename according to the pattern ($1 is the 
                       version number):
            'calpont-infinidb-ent-(.*).(x86_64.bin|amd64.deb|x86_64.rpm).tar.gz'
        
        @raises      - exception if the input file path is malformed.
        '''
        f = os.path.split(pfile)[1]
        m = self._verspatt.match(f)
        if not m:
            raise Exception("%s does not look like a package file!" % pfile)
        return m.group(3)

    def match(self, ptype, pfile):
        return self._filepatt[ptype].match(pfile)
