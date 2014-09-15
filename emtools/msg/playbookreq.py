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
emtools.msg.playbookreq

contains:
    class PlaybookRequest
'''

from jsonmsg import JsonMsg
import json

class PlaybookRequest(JsonMsg):
    '''
    Message sent by the server to initiate a playbook.
    
    Equivalent Thrift Message spec:
    
    struct PlaybookInfo {
        1: required string  name;
        2: required string  hostspec;
        2: optional string  extravars;
    }
    
    struct PlaybookRequest {
        1: required string  cluster_name;             // cluster name
        2: required PlaybookInfo playbook_info;       // playbook info
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
                "playbook_info" : {
                    "type":"object",
                    "properties" : {
                        "name" : { "type" : "string", "blank" : False },
                        "hostspec" : { "type" : "string", "blank" : False },
                        "extravars" : { "type" : "string" },                        
                    }                               
                }         
            }
        }
        
        JsonMsg.__init__( self, jsonstring, self.__schema )

def PlaybookRequest_from_dict( inv_dict ):
    return PlaybookRequest( json.dumps( inv_dict ) )