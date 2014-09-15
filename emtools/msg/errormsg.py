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
emtools.msg.errormsg

contains:
    class ErrorMsg
'''

from jsonmsg import JsonMsg
import json

class ErrorMsg(JsonMsg,BaseException):
    '''
    Error message returned by all utilities.
    
    Equivalent Thrift Message spec:
    
    struct ErrorMsg {
        1: required bool         failed;  // should be true
        2: required string       msg;     // descriptive error msg
        3: optional string       cmd;     // cmd if error occurred during execution
        3: optional int          rc;      // command return code if applicable
        4: optional string       stdout;  // stdout if applicable
        5: optional string       stderr;  // stderr if applicable
    }
    '''

    def __init__(self, jsonstring):
        '''
        Constructor.
        '''
        self.__schema = { 
            "type":"object",
            "properties": {
                "failed":{
                    "type":"boolean",
                    "blank":False
                },
                "msg":{
                    "type":"string",
                    "blank":False
                },
                "cmd":{
                    "type":"string",
                    "required":False
                },
                "rc":{
                    "type":"integer",
                    "required":False
                },
                "stdout":{
                    "type":"string",
                    "required":False
                },
                "stderr":{
                    "type":"string",
                    "required":False
                },
            }
        }
        
        JsonMsg.__init__( self, jsonstring, self.__schema )

def ErrorMsg_from_parms( msg, cmd=None, rc=None, stdout=None, stderr=None):
    errordict = {
        "failed": True,
        "msg" : msg
    }
    if cmd is not None:
        errordict['cmd'] = cmd
    if rc is not None:
        errordict['rc'] = rc
    if stdout is not None:
        errordict['stdout'] = stdout
    if stderr is not None:
        errordict['stderr'] = stderr
    return ErrorMsg( json.dumps( errordict ) )
