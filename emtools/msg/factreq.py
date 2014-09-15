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
emtools.factreq

contains:
    class FactRequest
'''

from jsonmsg import JsonMsg
import json

class FactRequest(JsonMsg):
    '''
    Message sent by the client during the install new cluster use case
    after the user has input a list of hostnames and access credentials.
    
    Equivalent Thrift Message spec:
    
    struct FactRequest {
        1: required string       cluster_name;
        2: required list<string> hostnames;
        3: required string       ssh_user; // ssh user
        4: optional string       ssh_key;  // ssh private key text
        5: optional string       ssh_pass; // ssh password
        6: optional i16          ssh_part; // ssh port
    }
    
    ADDITIONAL VALIDATION: 
      - hostnames must contain at least one item.
      - cluster_name and ssu_user cannot be empty.
      - exactly one of ssh_key and ssh_pass must be present
    '''

    def __init__(self, jsonstring):
        '''
        Constructor.
        '''
        self.__schema = { 
            "type":"object",
            "properties": {
                "cluster_name":{
                    "type":"string",
                    "blank":False
                },
                "hostnames": {
                    "items": {
                        "type":"string"
                    },
                    "minItems": 1
                },
                "ssh_user":{
                    "type":"string",
                    "blank":False
                },
                "ssh_key":{
                    "type":"string",
                    "required": False
                },
                "ssh_pass":{
                    "type":"string",
                    "required": False
                },
                "ssh-port":{
                    "type":"integer",
                    "required": False
                }
            }
        }
        
        JsonMsg.__init__( self, jsonstring, self.__schema )
        if ( self.has_key('ssh_key') and self.has_key('ssh_pass') ) or\
            ( not self.has_key('ssh_key') and not self.has_key('ssh_pass') ):
            raise Exception('FoctRequest ERROR - exactly one of ssh_key, ssh_pass must be present')

def FactRequest_from_dict( factrequest_dict ):
    return FactRequest( json.dumps( factrequest_dict ) )
