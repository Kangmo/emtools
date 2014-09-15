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
emtools.msg.factreply

contains:
    class FactReply
'''

from jsonmsg import JsonMsg
import json

class FactReply(JsonMsg):
    '''
    Message sent by the server in response to the FactReq message.
    
    Equivalent Thrift Message spec:
    
    struct ClusterInfo {
        1: required bool         valid;               // At least 1 reachable node.  All reachable nodes are same OS family
        2: required string       name;                // cluster name (null if not existing idb or em install)
        3: required string       os_family;           // if valid = true, set to cluster os_family
        4: required string       gluster_version;     // non-null indicates presence of gluster on 1 or more nodes
        5: required string       hadoop_version;      // non-null indicates presence of hadoop on 1 or more nodes
        6: required string       infinidb_version;    // non-null indicates presence of infinidb on 1 or more nodes
        7: required string       em_version;          // non-null indicates presence of em on 1 or more nodes
        8: optional string       reason;              // if not valid, explains why
    }
    
    struct InstanceInfo {
        1: required bool         valid;               // is node reachable
        2: required string       ip_address;          // ip address
        3: required string       gluster_version;     // non-null indicates presence of gluster
        4: required string       hadoop_version;      // non-null indicates presence of hadoop
        5: optional string       reason;              // if not valid, explains why
    }

    struct FactReply {
        1: required ClusterInfo  cluster_info;        // cluster level summary information
        2: required map<string,InstanceInfo> instance_info; // instance attributes 
        3: required map<string,string>       role_info; // map from role name to instance hostname
                                                      // valid role names are
                                                      //   pmX
                                                      //   umX
                                                      //   oam_server
                                                      //   oam_agent
    }
    
    ADDITIONAL VALIDATION: 
      - instance_info must contain at least one item.
    '''
    
    def __init__(self, jsonstring):
        '''
        Constructor.
        '''
        self.__schema = { 
            "type":"object",
            "properties": {
                "cluster_info" : {
                    "type":"object",
                    "properties": {
                        "valid" : { "type": "boolean" },
                        "name" : { "type": "string" },
                        "os_family" : { "type": "string" },
                        "gluster_version" : { "type": "string"  },
                        "hadoop_version" : { "type": "string" },
                        "infinidb_version" : { "type": "string" },
                        "em_version" : { "type": "string" },
                        "reason"     : { "type": "string", "required" : False }
                    }
                },
                "instance_info" : {
                    "type":"object",
                    "items": {
                        "type":"object",
                        "properties": {    
                            "valid" : { "type": "boolean" },
                            "ip_address" : { "type": "string" },
                            "gluster_version" : { "type": "string"  },
                            "hadoop_version" : { "type": "string" },
                            "reason"     : { "type": "string", "required" : False }
                        }
                    }
                },
                "role_info" : {
                    "type":"object"                               
                }         
            }
        }
        
        JsonMsg.__init__( self, jsonstring, self.__schema )

def FactReply_from_dict( factreply_dict ):
    return FactReply( json.dumps( factreply_dict ) )
    
