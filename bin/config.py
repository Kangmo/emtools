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

#!/usr/bin/env python
'''
config.py

Accepts a config request message as input and produces a config Reply
'''
import getopt
import os, sys

from emtools.playbookmgr import PlaybookMgr
import emtools.msg.configreq as configreq
import emtools.common.properties as properties
import emtools.msg.configreply as configreply
import emtools.msg.errormsg as errormsg
import emtools.idbxml as idbxml
import validictory
import json
import emtools.common.logutils as logutils

# roll this version for any significant changes
version = '0.1'

class ConfigGetter(object):
    def __init__(self, req):
        self.__req = req
        self.__pmgr = PlaybookMgr( req['cluster_name'] )
        schema = { 
            "type":"object",
            "properties": {
                "infinidbconfig": {
                    "items": {
                        "type":"object",
                            "properties":{    
                            "xml_section":{
                                "type":"string",
                                "required":False
                            },
                            "xml_parameter": {
                                "type":"string",
                                "required":False
                            },
                            "default":{
                                "type":"string",
                                "required":False
                            },
                            "description":{
                                "type":"string",
                                "blank": False
                            },
                            "em_category":{
                                "type":"string",
                                "required": False
                            },
                            "em_parameter":{
                                "type":"string",
                                "required": False
                            },
                            "value":{
                                "type":"string",
                                "required": False
                            }
                        }
                    },
                    "minItems": 1
                }
            }
        }
        props = properties.Properties()
        filepath = '%s/config.json'% props['emtools.confdir']
        #print filepath
        try:
            mapfile = open( filepath )
            self.__data = json.load( mapfile )
            validator = validictory.validator.SchemaValidator(blank_by_default=True)
            validator.validate( self.__data, schema )
        except Exception, exc:
            msg = 'Error loading config.json: %s' % exc
            e = errormsg.ErrorMsg_from_parms(msg=msg)
            print e
            sys.exit(1)
        
    def run(self, req):
        #for a in req['set_params']:
            #print a
        if req['action'].lower() == 'get':
            rc, results, out, err = self.__pmgr.run_playbook('getinfo.yml', 'infinidb', 'pm1')
            if rc == 0:         
                parmInfos = []     
                xml = idbxml.IdbXml( '%s/cluster_files/Calpont.xml' % (self.__pmgr.get_rootdir()) )
                for w in self.__data["infinidbconfig"]:
                    value = xml.get_parm( w["xml_section"],w["xml_parameter"] )
                    param_info = dict(
                        em_category=w["em_category"],
                        em_parameter=w["xml_parameter"],
                        value=value,
                        description=w["description"]
                    )
                    parmInfos.append( param_info )
            else:
                return errormsg.ErrorMsg_from_parms(msg="run_playbook getinfo failed",
                                                    rc=rc,
                                                    stdout=out,
                                                    stderr=err)
            reply = configreply.ConfigReply_from_dict( { "cluster_name" : req['cluster_name'], "config" : parmInfos} )        
        elif req['action'].lower() == 'set':
            parmInfos = []
            for parms in req['set_params']:
                #get the section name in Calpont.xml
                for w in self.__data["infinidbconfig"]:
                    if w["em_parameter"].lower() == parms['em_parameter'].lower():
                        break
                
                values = ' ' + w["xml_section"] + ' ' + w['xml_parameter'] + ' ' + parms['value']
                
                try:
                    # we don't need the return value.  If it fails we catch the exception
                    # if it works then we know the value was set
                    cmdstr = '{{ infinidb_installdir }}/bin/setConfig %s' % values

                    self.__pmgr.run_module( 'infinidb', 'pm1', 'command', cmdstr, sudo=False )
                except errormsg.ErrorMsg, exc:
                    return exc
                              
                param_info = dict(
                    em_category=parms["em_category"],
                    em_parameter=parms['em_parameter'],
                    value=parms['value'],
                )
                parmInfos.append( param_info )                   
                
            reply = configreply.ConfigReply_from_dict( { "cluster_name" : req['cluster_name'], "config" : parmInfos} )  
        else:
            reply = errormsg.ErrorMsg_from_parms(msg="config requires an action string: get or set")            
            
        return reply  
#-------------------------------------------------------------------------------
def usage():
    '''
    Print command line usage
    '''
    print 'config.py [hvs] [--json=]'
    print ''
    print 'Version: %s' % version
    print ''
    print 'This is a utility that performs the get and set Calpont.xml.  There are'
    print 'two ways to use it.  Either a file name needs to be specified via'
    print 'the --json option, or stdin of the request json is used'
    print ''
    print '    -h            show help'
    print '    -v            print version'
    print '    -i            use stdin to input request message'
    print '    --json <file> use request message specified in <file>'

#-------------------------------------------------------------------------------
def main(argv):
    '''
    main function
    '''
    
    try:                                
        opts, args = getopt.getopt(argv, "hvi", ['json='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)   
    
    # defaults
    use_stdin = False
    json_file = ''
    
    for o,a in opts:
        if o == '-h':
            usage()
            sys.exit(2)
        elif o == '-v':
            print 'launch.py Version: %s' % version
            sys.exit(1)
        elif o == '-i':
            use_stdin = True
        elif o == '--json':
            json_file = a
        else:
            print 'unsupported option: %s' % o
            usage()
            sys.exit(2)
        
    jsonstr = None
    if json_file:
        f = open( json_file )
        lines = f.readlines()
        jsonstr = ''.join(lines)
    elif use_stdin:
        lines = sys.stdin.readlines()
        jsonstr = ''.join(lines)
    else:
        print 'need cluster name'
        usage()
        sys.exit(2)
        
    #print jsonstr       
    req = configreq.ConfigRequest(jsonstr)

    Log = logutils.getLogger('config')
    Log.info('request: %s' % req.json_dumps())

    fget = ConfigGetter( req )
    reply = fget.run( req )

    Log.info('reply: %s' % reply.json_dumps())
    print reply
       
    if reply.has_key('rc'):
        return reply['rc']
    else:
        return 0
    
#-------------------------------------------------------------------------------
# main entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
