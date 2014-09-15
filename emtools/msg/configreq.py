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
eminstall.configreq

contains:
    class ConfigRequest
'''

from jsonmsg import JsonMsg
import json

class ConfigRequest(JsonMsg):
    '''
    Message sent by the client 
    
    Equivalent Thrift Message spec:
    {
        "cluster_name": "tester",
        "action": "get",
        "set_params":[
            { "em_category" : "UM",
            "em_parameter" : "TotalUmMemory",
            "value" : "2G" },
            { "em_category" : "PM",
            "em_parameter" : "PmMaxMemorySmallSide",
            "value" : "64M" }
        ]
    }
    
    struct ParmInfo {
        1: required string       em_category;         // the cataegory of the parameter, e.g., UM or PM
        2: required string       em_parameter;        // the parameter name
        3: required string       value;               // the value of parameter
    }
    
    struct ConfigRequest {
        1: required string       cluster_name;
        2: required string       action
        3: optional list         ParmInfos
    }
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
                "action":{
                    "type":"string",
                    "blank":False
                },
                "set_params":{
                    "required":False,
                    "items": {
                        "type":"object",
                        "properties": {
                            "em_category" : { "type": "string" },
                            "em_parameter" : { "type": "string" },
                            "value" : { "type": "string"  }
                        }
                    },
                    "minItems": 0 
                }
            }
        }   
        #print "jason string " +jsonstring
        JsonMsg.__init__( self, jsonstring, self.__schema )
        if ( not self.has_key('action') ):
            raise Exception('ConfigRequest ERROR - exactly one of action must be present')

def ConfigRequest_from_dict( configrequest_dict ):
    return ConfigRequest( json.dumps( configrequest_dict ) )
