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
emtools.msg.commandreq

contains:
    class CommandReq
'''

from jsonmsg import JsonMsg
import json

class CommandReq(JsonMsg):
    '''
    Message sent to issue a calpontConsole command.
    
    Equivalent Thrift Message spec:
    
    struct CommandReq {
        1: required string       cluster_name;
        2: required string       command;  // calpontConsole command
        3: optional string       args;     // command arguments
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
                "command":{
                    "type":"string",
                    "blank":False
                },
                "args":{
                    "type":"string",
                    "required":False
                },
            }
        }
        
        JsonMsg.__init__( self, jsonstring, self.__schema )

def CommandReq_from_dict( factrequest_dict ):
    return CommandReq( json.dumps( factrequest_dict ) )
