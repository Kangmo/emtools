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
eminstall.idbxml

Contains:
    class IdbXml
'''

import xml.etree.ElementTree as ET

class IdbXml(object):
    '''
    IdbXml parses Calpont XML and derives various important information.
    '''

    def __init__(self, file_):
        '''
        Constructor.
        
        :param file_: Calpont.xml file to parse
        '''
        self.parse( file_ )
        
    def parse(self, file_):
        '''
        Parses a Calpont.xml file.
        
        :param file_: Calpont.xml file to parse
        '''
        self.__file = file_
        self.__root = ET.parse( file_ ).getroot()
        
    def get_all_roles(self):
        '''
        Returns a list of all role assignments.  Each entry in the list is
        a dict with role= and ip_address= keys.
        '''        
        return self.get_pms() + self.get_ums()
    
    def get_pms(self):
        '''
        Returns a list of all pm role assignments.  Each entry in the list 
        is a dict with role= and ip_address= keys.
        '''
        ret = []

        # first figure out how many UMs we have
        ps = self.__root.find('SystemModuleConfig')
        count = int( ps.find('ModuleCount3').text )

        # now loop through each PM
        for i in range(1, count+1):
            iptag = 'ModuleIPAddr%d-1-3' % i
            pm_ip = ps.find( iptag )
            hosttag = 'ModuleHostName%d-1-3' % i
            pm_host = ps.find(hosttag)
            ret.append( dict( role='pm%d' % i, ip_address=pm_ip.text, hostname=pm_host.text ) )
            
        return ret
    
    def get_ums(self):
        '''
        Returns a list of all um role assignments.  Each entry in the list 
        is a dict with role= and ip_address= keys.
        '''
        ret = []
        
        # first figure out how many UMs we have
        ps = self.__root.find('SystemModuleConfig')
        count = int( ps.find('ModuleCount2').text )

        # now loop through each PM
        for i in range(1, count+1):
            iptag = 'ModuleIPAddr%d-1-2' % i
            um_ip = ps.find( iptag )
            hosttag = 'ModuleHostName%d-1-2' % i
            um_host = ps.find(hosttag)
            ret.append( dict( role='um%d' % i, ip_address=um_ip.text, hostname=um_host.text ) )

        return ret
        
    def get_parm(self, section, parmname):   
        '''
        Returns the value of parmname in section in Calpont.xml.
        
        :param section: secion name in Calpont.xml
        :param parmname: parameter name in the section in Calpont.xml
        '''     
        ps = self.__root.find(section)
        if ps is None:
            return ''
        value = ps.find(parmname)
        if value is None:
            return ''
        return value.text
        
        
