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
emtools.vmi.versionmgr

Interact with the infinidb database package directory.
'''
import os
import re
import emtools.common as common
from pkgfilenameparser import PkgFileNameParser

class EmVersionManager(object):
    '''
    Simplified version of versionmgr.py found in autooam.
    This class finds the tar ball file to be used in a db install.
    '''

    def __init__(self):
        '''
        Constructor.
        
        Ensure that package directory exists.
        '''
        self._basedir = common.props['cluster.emversionmgr.packages_base']
        
        if not os.path.exists(self._basedir):
            raise Exception("Package reference directory %s does not exist!" % self._basedir) 
        
        self._pkgfilenameparser = PkgFileNameParser()
        
    def retrieve(self, version, ptype):
        '''locates the specified package type.

        @param version - version to retrieve.
        @param ptype   - package type.  One of 'bin', 'deb', or 'rpm'
        Returns the relative path to the package tarball which is
        guaranteed to be located in /opt/infinidb/em/packages/database.
        
        Raises exceptions on failure to locate the specified package
        (or other misc. errors such as a bad type, etc.).
        '''        
        if not ptype in ['binary']: # presently only support binary
            raise Exception("Unsupported package type %s!" % ptype)

        # search for applicable pkg in self._basedir
        for p in os.listdir(self._basedir):
            mat = self._pkgfilenameparser.match(ptype,p)
            if mat and (self._pkgfilenameparser.get_pkg_version(p) == version):
                return p

        raise Exception("No %s package found in %s for version %s" %
            (ptype, self._basedir, version))
