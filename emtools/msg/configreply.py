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
emtools.msg.configreply

contains:
    class ConfigReply
'''

from jsonmsg import JsonMsg
import json

class ConfigReply(JsonMsg):
    '''
    Message sent by the server in response to the ConfigReq message.
    
    Equivalent Thrift Message spec:
    
    [
        { "em_category" : "UM",
          "em_parameter" : "TotalUmMemory",
          "value" : "2G" },
        { "em_category" : "PM",
          "em_parameter" : "PmMaxMemorySmallSide",
          "value" : "64M" }
    ]
    
    struct ParmInfo {
        1: required string       em_category;         // the cataegory of the parameter, e.g., UM or PM
        2: required string       em_parameter;        // the parameter name
        3: required string       value;               // the value of parameter
    }

    struct ConfigReply {
        1: required list of ParmInfo;        // parameter information
    }
    '''
    
    def __init__(self, jsonstring):
        '''
        Constructor.
        '''
        self.__schema = { 
            "type":"object",
            "properties": {
                "cluster_name" : { "type": "string" }, 
                "config" : {
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
        
        JsonMsg.__init__( self, jsonstring, self.__schema )

def ConfigReply_from_dict( configreply_dict ):
    return ConfigReply( json.dumps( configreply_dict ) )
    
