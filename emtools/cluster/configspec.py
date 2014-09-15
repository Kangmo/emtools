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
emtools.cluster.configspec

Represents desired configuration for a cluster used to execute a test.  
Manages JSON decoding and validation 
'''
import json
import emtools.common as common
import re
import emtools.common.logutils as logutils

Log = logutils.getLogger(__name__)

class ConfigSpec(object):
    """
    The ConfigSpec class is designed to be a loose wrapper around JSON
    object specifications for the purpose of specifying an autooaom 
    cluster configuration.  The class requires that the JSON root object
    is a map and makes that available via the config() method.  It also
    does validation against mandatory attributes and raises an exception 
    if a mandatory attribute is not present in the constructor
    
    Methods:
    __getitem__(self, key) - access a value via []
    __setitem__(self, key, value) - set a value via []
    json_dumps(self) - dump a JSON string for the current config map
    
    Mandatory Root Attributes:
    ['name']          - Name used to refer to the cluster config - recommended 
                        to be unique and descriptive.
    ['rolespec']      - must be a map of maps where one map corresponds to
                        one role (either 'pm' or 'um').  A 'pm' role is
                        required.  If a 'um' role is present, the system is
                        a 'separate' system, otherwise it is a 'combined'
                        system.
    ['idbversion']    - version of infinidb to use.  This item is mandatory at 
                        construction time but may be passed in as named arguments 
                        to the constructor. 
    ['boxtype']       - which vagrant box type to use for the base machine.  This 
                        item is mandatory for vagrant configs but is not checked 
                        at construction time.
    
    Optional Root Attributes:
    ['idbuser']       - which user to use for the owner of the infinidb install.
                        If not set, the user defaults to root and the standard
                        rpm/deb install is used.  If not root, then the specified 
                        user name will be created and used and a non-root binary
                        install will be used.  The value 'root' is disallowed.
    ['datdup']        - whether or not to configure the datdup package (i.e.
                        data duplication/glusterfs).  The value must be one of the
                        boolean values: true or false (non-quoted)
    ['binary']        - whether or not to use a binary install even if the user
                        is 'root'.  If false, the default package type is used
                        based on the user (root = rpm/deb, non-root=binary).  If
                        true, then both user types will be binary.
    ['storage']      -  DBRoot storage type.  Current values are 'internal'
                        and 'external'.  Default is 'internal'.
    ['upgrade']      -  Default in ''.  When specified this is a string 
                        identifying the version of InfiniDB that will be upgrade to.
    ['hadoop']       -  When present, a map containing configuration information 
                        passed through to Whirr to do the Hadoop install.
                        Required members (in autooam test mode only, else n/a):
                          instance-templates - string passed to whirr.instance-templates
                        Optional members:
                          version            - string passed to whirr.hadoop.version 
                          templates-namenode - string defining servers to be assigned
                                               namenode/jobtracker roles.  Passed to
                                               whirr.templates.<roles>.byon-instance-ids
                          templates-datanode - string defining servers to be assigned
                                               datanode/tasktracker roles.  Passed to
                                               whirr.templates.<roles>.byon-instance-ids
    ['enterprise']    - whether or not to configure the enterprise add-on package 
                        in 4.0 and later versions.  The value defaults to true for 
                        backwards compatibility and the value must be one of the
                        boolean values: true or false (non-quoted)
    ['pm_query']      - whether the PM with local query option is enabled.  The option
                        is only applicable in 4.5 or later versions.  It defaults to false
                        for backwards compatibility and the value must be one of the
                        boolean values: true or false (non-quoted)
    ['em']           -  When present, a map containing configuration information 
                        for the enterprise manager to be used for the cluster.
                        Required members:
                          present            - boolean indicating that an EM is present
                                               and should attempt an attach to the cluster
                                               under test.
                        Optional members:
                          emhost             - string of the EM host to use.  If not
                                               specified uses the cluster.cluster.emhost
                                               property. 
                          emport             - port number of the EM host to use.  If not
                                               specified uses the cluster.cluster.emport
                                               property. 
                          oamserver_role     - role name (umX, pmX) to use as the oam_server.
                                               If not specified defaults to um1
                          invm               - boolean indicating if the vmi should spawn
                                               a dedicated VM to run the EM.  If not set
                                               uses the cluster.cluster.eminvm property.
                                               If create is true then emhost is overridden 
                                               when the VMI creates the instance for the EM.
                        Optional members if 'invm' is true:
                          boxtype            - box type for enterprise manager
                                               (default is same as rest of cluster)
                          version            - version for enterprise manager
                                               (default is Latest)
                          role               - the server where EM is to be installed
                                               (default is 'um1')
                        
    rolespec specification (um/pm):
    ['count']         - required int attribute that specifies the number of
                        pm nodes (or combined nodes if no um spec)
    ['dbroots_per']   - int value specifying how many db roots per pm.  This
                        is one of two possible ways to assign dbroot values.
                        Using this option, an equal number of dbroots is 
                        assigned to each pm in sequential increasing numbers
                        starting at 1. (pm-only)
    ['dbroots_list']  - list of lists specifying explicit dbroots per pm.  The
                        length of the outer list must match the pm count.  The
                        length of the inner lists may vary and contain lists of
                        integers representing dbroot numbers. (pm-only)
    ['memory']        - optional int attribute specifying the memory to request
                        for this role type
    ['cpus']          - optional int attribute specifying the # of cpus to request
                        for this role type
    
    """ 

    def __init__(self, jsonstring=None, jsonfile=None, idbversion=None, boxtype=None):
        '''Constructor.
        
        @param jsonstring - JSON string specifying the configuration
        @param jsonfile   - JSON filename containing the configuration
        @param idbversion - set/override the idbversion
        @param boxtype    - set/override the boxtype 
        
        Raises an exception if mandatory attributes not part of the JSON
        specification or if the root object is not a map.
        '''
        if jsonfile:
            self.jsonmap = json.load(open(jsonfile))
        else:
            self.jsonmap = json.loads(jsonstring)
            
        if not type(self.jsonmap) is dict:
            raise Exception("Root ConfigSpec JSON specification not a map!")
        
        if idbversion:
            self.jsonmap['idbversion'] = u'%s' % idbversion
        if boxtype:
            self.jsonmap['boxtype'] = u'%s' % boxtype            
        
        # this is a list of all the supported root-level attributes.  The tuple
        # values represent:
        #   ( <name>, <type>, <required>, <default value> )
        #        name          = attribute name
        #        type          = Python type designation
        #        required      = boolean value indicating whether the attribute is required
        #        default value = for non-required attributes, the default value
        #                        that should be present if not specified.
        root_attr_list = [
            ('name', unicode, True, None),
            ('idbversion', unicode, True, None), 
            ('rolespec', dict, True, None),
            ('idbuser', unicode, False, u'root'),
            ('datdup', bool, False, False),
            ('binary', bool, False, False),
            ('storage', unicode, False, u'internal'),
            ('upgrade', unicode, False, u''),
            ('hadoop', dict, False, None),
            ('enterprise', bool, False, True),
            ('pm_query', bool, False, False),
            ('em', dict, False, None),
            ]

        for attr in root_attr_list:
            self._attr_check(self.jsonmap, attr[0], attr[1], attr[2], attr[3])
        self._check_rolespec(self.jsonmap['rolespec'])
            
        # em is special in that we have a global property that determines 
        # whether we should always use an em section
        # TODO - need to update the list of supported box types once EM
        # support for Ubuntu/Debian is worked out
        if ( common.props['cluster.cluster.empresent'] or common.props['cluster.cluster.eminvm'] ) and\
            not self.jsonmap['em']:
                embox = common.props['cluster.cluster.emboxtype']
                if not ConfigSpec._version_greaterthan(self.jsonmap['idbversion'], '4.5.0-0' ):
                    Log.warn('EM requested, but not supported in InfiniDB version %s!' % self.jsonmap['idbversion'] )
                else:
                    self.jsonmap['em'] = { "present" : True }
        if self.jsonmap['em']:
            self._check_em(self.jsonmap['em'])

    def validate(self):
        """Checks various version, platform dependencies to see whether the config is valid."""
        if self.jsonmap['datdup']:
            # config specifies datdup.  We technically supported since 3.5.1, but 
            # prefer to officially support as of 4.0.0
            # technically there may be box restrictions as well, but that is really
            # dependent on the mechanism we use to install gluster
            if not ConfigSpec._version_greaterthan(self.jsonmap['idbversion'], '4.0.0-0' ):
                raise Exception('datdup only supported in versions 3.5.1-5 and later')
            if self.jsonmap['storage'] != 'internal':
                raise Exception('datdup only supported for internal storage')
        if self.jsonmap['idbuser'] != 'root':
            if not ConfigSpec._version_greaterthan(self.jsonmap['idbversion'], '3.5.1-5' ):
                raise Exception('non-root user only supported in versions 3.5.1-5 and later')
        if self.jsonmap['hadoop']:
            if not ConfigSpec._version_greaterthan(self.jsonmap['idbversion'], '4.0.0-0' ):
                raise Exception('Hadoop only supported in versions 4.0.0-1 and later')
        if self.jsonmap['pm_query']:
            if not ConfigSpec._version_greaterthan(self.jsonmap['idbversion'], '4.5.0-0' ):
                raise Exception('PM local query option only supported in versions 4.5.x and later')
        # TODO-think about this.  EM has partial functionality for other versions
        if self.jsonmap['em'] and self.jsonmap['em']['present']:
            if not ConfigSpec._version_greaterthan(self.jsonmap['idbversion'], '4.5.0-0' ):
                raise Exception('Enterprise Manager attach option only supported in versions 4.5.x and later')
        return True        

    def infinidb_install_dir(self):
        if self.jsonmap['idbuser'] == 'root':
            return '/usr/local/Calpont'
        else:
            return '/home/%s/Calpont' % self.jsonmap['idbuser']
     
    @classmethod
    def _version_cmp(cls,version,minver):
        if version == minver:
            return 0
        elif ConfigSpec._version_greaterthan(version, minver):
            return 1
        else:
            return -1

    @classmethod
    def _version_greaterthan(cls,version,minver):
        # check special cases around 'Latest' first
        if version == 'Latest':
            # latest means trunk nightly which be definition is always >
            return True
        elif minver == 'Latest':
            # any compare against Latest (except Latest > Latest) is false
            return False
        
        thisver = cls._convert_to_ver_tuple(version)
        min_ = cls._convert_to_ver_tuple(minver)
        # check major version first
        if thisver[0][0] < min_[0][0]:
            return False
        elif thisver[0][0] > min_[0][0]:
            return True
        
        # guaranteed Major == Major, now minor version
        if thisver[0][1] < min_[0][1]:
            return False
        elif thisver[0][1] > min_[0][1]:
            return True
        
        # guaranteed Major == Major and Minor == Minor
        if len(thisver[0]) == 2:
            # special case for nightly, always latest on its stream
            return True
        elif len(min_[0]) == 2:
            # no way version is greater if more specifiers than X.Y
            return False
        elif thisver[0][2] < min_[0][2]:
            return False
        elif thisver[0][2] > min_[0][2]:
            return True

        # guaranteed Major == Major and Minor == Minor and dot1==dot1
        if len(thisver[0]) != len(min_[0]):
            # longer version is always greater than shorter
            return len(thisver[0]) > len(min_[0])
        elif len(thisver[0]) == 3:
            # both inputs had only 3 parts so need to check dash part
            if thisver[1] != None and min_[1] != None:
                # they both had a dash
                if thisver[1] == min_[1]:
                    # dash numbers are equal.  need to check any extra text - extra text
                    # is always less than any without
                    if thisver[2] != None and min_[2] == None:
                        return False
                    elif thisver[2] == None and min_[2] != None:
                        return True
                    else:
                        return thisver[2] >= min_[2]
                else:
                    return thisver[1] >= min_[1]
            elif thisver[1] == None and min_[1] == None:
                return True
            else:
                return thisver[1] != None
        elif thisver[0][3] < min_[0][3]:
            return False
        elif thisver[0][3] > min_[0][3]:
            return True

        # guaranteed Major == Major and Minor == Minor and dot1==dot1 and dot2==dot2
        if thisver[1] != None and min_[1] != None:
            # they both had a dash
            if thisver[1] == min_[1]:
                # dash numbers are equal.  need to check any extra text - extra text
                # is always less than any without
                if thisver[2] != None and min_[2] == None:
                    return False
                elif thisver[2] == None and min_[2] != None:
                    return True
                else:
                    return thisver[2] >= min_[2]
            else:
                return thisver[1] >= min_[1]
        elif thisver[1] == None and min_[1] == None:
            return True
        else:
            return thisver[1] != None
        
    @classmethod
    def _convert_to_ver_tuple(cls, vers):

        # there are occasionally non-standard names that show up in the
        # packages area - ex. 4.0.0-1_old. We need to be able to detect
        # that and make sure the version still gets processed correctly.
        extra = re.compile('.*[0-9]([\-_a-zA-Z]+)$')
        extratext = None
        mat = extra.match(vers)
        if( vers != 'Latest' and mat):
            vers = vers[0:len(vers) - len(mat.group(1))]
            extratext = mat.group(1)
            
        outerparts = vers.split('-')
        innerparts = outerparts[0].split('.')

        try:
            innerints = [int(numeric_string) for numeric_string in innerparts]
        except:
            # this is a strange case that could happen trying to process
            # directory names in the package area that aren't traditionally formed
            # setting to some bogus value here should be ok
            innerints = [ 99, 99 ]
        
        if len(innerparts) < 2:
            raise Exception('A version must at least have <major>.<minor>: %s' % vers)
        dash = None
        if len(outerparts) > 1:
            dash = int(outerparts[1])
        return (innerints, dash, extratext)
        
    def has_key(self, key):
        """Returns bool indicating whether or not the key exists in the map."""
        return self.jsonmap.has_key(key)
    
    def __getitem__(self, key):
        """Returns an item from the map."""
        return self.jsonmap[key]

    def __setitem__(self, key, value):
        """Sets an item in the map."""
        self.jsonmap[key] = value
        
    def json_dumps(self):
        """Dumps the map as a JSON encoded string."""
        return json.dumps(self.jsonmap)

    def total_dbroot_count(self):
        """
        Return the total DBRoot count for a cluster based
        on the number of DBRoots per PM and the number of PMs.
        """
        # TODO-this code only works for the dbroots_per setting, not if 
        # dbroots were specified with the dbroots_list option
        rootCount = (self['rolespec']['pm']['count'] *
            self['rolespec']['pm']['dbroots_per'])
        return rootCount
    
    def total_pm_count(self):
        """
        Return the total PMs
        """
        pmCount = self['rolespec']['pm']['count']
        return pmCount
    
    def total_um_count(self):
        """
        Return the total UMs
        """
        if not self['rolespec'].has_key('um'):
            return 0
        
        umCount = self['rolespec']['um']['count']
        return umCount
    
    def _check_rolespec(self, rolespec):
        # a pm role is required
        if not rolespec.has_key('pm'):
            raise Exception("rolespec does not specify a pm role!")
        
        pm = rolespec['pm']
        # must be one or more pms
        self._attr_check(pm, 'count', int, True, None)
        if pm['count'] < 1:
            raise Exception("Must have at least 1 pm role!")
        
        # must have one of dbroots_per or dbroots_list
        if pm.has_key('dbroots_per'):
            if not type(pm['dbroots_per']) is int or pm['dbroots_per'] < 1:
                raise Exception("Must have at least 1 dbroot per pm!")
            if pm.has_key('dbroots_list'):
                raise Exception("Cannot specify both dbroots_per and dbroots_list!")                
        elif pm.has_key('dbroots_list'):
            if not type(pm['dbroots_list']) is list:
                raise Exception("dbroots_list must be a list!")
            if len(pm['dbroots_list']) != pm['count']:
                raise Exception("Length of dbroots_list must match pm count!")
            for i in range(0, len(pm['dbroots_list'])):
                if not type(pm['dbroots_list'][i]) is list:                 
                    raise Exception("dbroots_list[%d] is not a list!" % i)
        else:
            raise Exception("Must specify either dbroots_per or dbroots_list!")
            
        rolect = 1                
        # now check the um - if present it must have count >= 1
        if rolespec.has_key('um'):
            rolect = 2
            self._attr_check(rolespec['um'], 'count', int, True, None)
            if rolespec['um']['count'] < 1:
                raise Exception("Must have at least 1 um role if present!")
        
        if rolect != len(rolespec):
            # this means there must be some other role specified that we don't know anything about
                raise Exception("Unknown role present - only pm and um supported!")

    def _attr_check(self, m, name, type_, required, default):
        """Private method.  Utility to validate presence and type of an attribute and possible set default values"""
        if required and not m.has_key(name):
            raise Exception("ConfigSpec did not specify required attribute " + name)
        if not m.has_key(name):
            m[name] = default
        elif m[name] and ( not type(m[name]) is type_ ):
            raise Exception("ConfigSpec has wrong type for attribute " + name)
        
    def _check_em(self, em):
        if not em.has_key('present'):
            raise Exception("Must specify present flag when specifying em")
        if not em.has_key('emhost'):
            self.jsonmap['em']['emhost'] = common.props['cluster.cluster.emhost']
        if not em.has_key('emport'):
            self.jsonmap['em']['emport'] = common.props['cluster.cluster.emport']
        if not em.has_key('oamserver_role'):
            self.jsonmap['em']['oamserver_role'] = common.props['cluster.cluster.oamserver_role']
        if not em.has_key('invm'):
            self.jsonmap['em']['invm'] = common.props['cluster.cluster.eminvm']
        if self.jsonmap['em']['invm']:
            # only care about the boxtype parm if the invm flag is True
            if not em.has_key('boxtype'):
                self.jsonmap['em']['boxtype'] = common.props['cluster.cluster.emboxtype']
            if not em.has_key('version'):
                self.jsonmap['em']['version'] = common.props['cluster.cluster.emversion']
            if not em.has_key('role'):
                self.jsonmap['em']['role'] = common.props['cluster.cluster.emrole']
