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
emtools.msg.inventoryreq

contains:
    class InventoryRequest
'''

from jsonmsg import JsonMsg
import json

class InventoryRequest(JsonMsg):
    '''
    Message sent by the server to create the 'infinidb' inventory.
    
    Equivalent Thrift Message spec:
    
    struct InventoryRequest {
        1: required string  cluster_name;             // cluster name
        3: required map<string,string> role_info;     // map from role name to instance hostname
                                                      // valid role names are
                                                      //   pmX
                                                      //   umX
                                                      //   oam_server
                                                      //   oam_agent
    }
    
    ADDITIONAL VALIDATION: 
      none
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
                "role_info" : {
                    "type":"object"                               
                }         
            }
        }
        
        JsonMsg.__init__( self, jsonstring, self.__schema )

def InventoryRequest_from_dict( inv_dict ):
    return InventoryRequest( json.dumps( inv_dict ) )
