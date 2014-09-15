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
emtools.common.properties

A class to manage property settings
'''
import os

from ConfigParser import ConfigParser

class Properties(object):
    '''
    The Properties class facilitates handling of an INI-style properties
    file using the Python ConfigParser object.  The general syntax is:
        [section]
        key=value
    
    By convention, emtools properties will be hierarchical '.'-style
    name corresponding to <package>.<property>.  For example:
       emtools.playbookmgr.cluster_base = '$INFINIDB_EM_TOOLS_HOME/clusters'
    '''
    
    def __init__(self, unittest = False, addtl_defns = None, addtl_site = None):
        '''
        Constructor.  Initializes the property set with defaults and then
        looks for a site.properties file in $AUTOOAM_HOME/conf and loads
        it if present
        '''    
        
        # these are the property definitions 
        self.__defns = {
            'emtools.playbookmgr.cluster_base':      (str, '%s/clusters' % (os.environ['INFINIDB_EM_TOOLS_HOME'])),
            'emtools.playbookmgr.playbook_template': (str, '%s/playbook_template' % (os.environ['INFINIDB_EM_TOOLS_HOME'])),
            'emtools.confdir':                       (str, '%s/conf' % (os.environ['INFINIDB_EM_TOOLS_HOME'])),
            'emtools.logname':                       (str, '%s/emtools.log' % os.environ['INFINIDB_EM_TOOLS_HOME']),
            'emtools.unittest':                      (bool, False),

            # for unit testing
            'emtools.test.user':                     (str, os.environ['USER']),
            'emtools.test.sshkeyfile':               (str, '%s/.ssh/id_rsa' % os.environ['HOME']),

            # em-related defaults for ConfigSpec
            'cluster.cluster.empresent':             (bool, False),
            'cluster.cluster.emhost':                (str, 'localhost'),
            'cluster.cluster.emport':                (int,  9090),
            'cluster.cluster.oamserver_role':        (str, 'um1'),
            'cluster.cluster.eminvm':                (bool, False),
            'cluster.cluster.emboxtype':             (str, 'cluster'), # special value 'cluster' means to use same box as rest of cluster
            'cluster.cluster.emversion':             (str, 'Latest'),
            'cluster.cluster.emrole':                (str, 'um1'),

            # where the emversionmgr will look for DB packages
            'cluster.emversionmgr.packages_base':    (str, '/opt/infinidb/em/packages/database'),
            }
        
        # we well set appropriate defaults here then allow override via
        # a site configuration file
        d = self.__dict__
        
        if addtl_defns:
            self.__defns = dict( self.__defns.items() + addtl_defns.items())
        for defn in self.__defns:
            d[defn] = self.__defns[defn][1]
            
        siteprops = '%s/conf/site.properties' % os.environ['INFINIDB_EM_TOOLS_HOME']
        if os.path.exists(siteprops) and not unittest:
            self.__loadPropFile(siteprops)
            
        if addtl_site and os.path.exists(addtl_site) and not unittest:
            self.__loadPropFile(addtl_site)
            
    # Used for unittest only, to test __loadPropFile()
    def test__loadPropFile(self, file_):
        return self.__loadPropFile(file_)

    def __loadPropFile(self, file_ ):
        """Loads properties file."""
        parser = ConfigParser()
        parser.read( file_ )
        if not parser.has_section('defaults'):
            raise Exception("ERROR-site.properties must have a [defaults] section")
        for o in parser.options('defaults'):
            if o == 'include':
                include = parser.get('defaults', o)
                if os.path.exists(include):
                    self.__loadPropFile( include )
            else:
                self.__setitem__(o, parser.get('defaults', o))
                              
    def __getitem__(self, key):
        """Returns an item from the map."""
        return self.__dict__[key]

    def __setitem__(self, key, value):
        """Sets an item in the map."""
        if not key in self.__defns:
            raise Exception("ERROR-unrecognized property %s" % key)
        else:
            defn = self.__defns[key]
            if defn[0] == bool:
                # special processing for boolean values
                if type(value) == bool:
                    pass
                elif value in ('False','false'):
                    value = False
                elif value in ('True','true'):
                    value = True
                else:
                    raise Exception("ERROR-non-boolean value %s specified for %s" % (value, key))
            elif defn[0] == int:
                try:
                    value = int(value)
                except Exception, exc:
                    raise Exception("ERROR-non-integer value %s specified for %s" % (value, key))
            elif defn[0] == str:
                if not ( type(value) == str or type(value) == unicode ):
                    raise Exception("ERROR-non-string value %s specified for %s" % (value, key))
            else:
                raise Exception("ERROR-unsupported property type %s" % defn[0])
                
            self.__dict__[key] = value

    def __contains__(self, key):
        """Tests for presence of key in the map."""
        if key in self.__dict__:
            return True
        else:
            return False

    def has_key(self, key):
        """Tests for presence of key in the map."""
        if key in self.__dict__:
            return True
        else:
            return False
