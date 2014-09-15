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
emtools.msg.installreq

contains:
    Class InstallReq
'''

from jsonmsg import JsonMsg
import json

class InstallReq(JsonMsg):
    '''
    Message sent by the server to initiate a new InfiniDB Cluster install.
    
    Equivalent Thrift Message spec:
    
    struct ClusterInfo {
        1: required string      infinidb_version;   // infinidb version to be installed
        2: required int         dbroots_per_pm;     // how many dbroots per PM
        3: optional [[int,.],[int,.].] dbroot_list; // nested array of ints; each inner
                                                    // array being a list of DBRoots for
                                                    // the corrresponding PM.
                                                    // For future use.  Not yet used.
        4: required string      infinidb_user;      // user used to install infinidb
        5: required string      storage_type;       // one of 'local', 'hdfs', 'gluster'
        6: required bool        pm_query;           // using or not using pm query feature
        7: required bool        um_replication;     // using or not using um replication feature
    }

    struct InstallReq {
        1: required string      cluster_name;       // cluster name
        2: required ClusterInfo cluster_info;       // cluster level summary information
        3: required map<string,string> role_info;   // maps role name to hostname
                                                    // (ex: pm1 -> 192.168.3.1)
    }
        '''

    def __init__(self, jsonstring):
        '''
        Constructor.
        '''
        self.__schema = {
            "type" : "object",
            "properties" : {
                "cluster_name" : { "type" : "string" },
                "cluster_info" : {
                    "type" : "object",
                    "properties" : {
                        "infinidb_version" : { "type": "string" },
                        "dbroots_per_pm"   : { "type": "integer"},
                        "dbroot_list"      : {
                            "type": "array",
                            "items" : {
                                "type" : "array"
                            },
                            "required": False
                        },
                        "infinidb_user"    : { "type": "string"  },
                        "storage_type"     : {
                            "enum": ["local","hdfs","gluster"]   },
                        "pm_query"         : { "type": "boolean" },
                        "um_replication"   : { "type": "boolean" }
                    }
                },
                "role_info" : { "type" : "object" }
            }
        }

        JsonMsg.__init__( self, jsonstring, self.__schema )

def InstallReq_from_dict( install_dict ):
    return InstallReq( json.dumps( install_dict ) )
