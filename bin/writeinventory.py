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
writeinventory.py

Reads an InventoryRequest and creates the 'infinidb' inventory file
'''
import getopt
import sys

from emtools.playbookmgr import PlaybookMgr
import emtools.msg.inventoryreq as inventoryreq
import emtools.msg.errormsg as errormsg
import json
import emtools.common.logutils as logutils

# roll this version for any significant changes
version = '0.1'

#-------------------------------------------------------------------------------
def usage():
    '''
    Print command line usage
    '''

    print 'writeinventory.py [hvi] [--json=]'
    print ''
    print 'Version: %s' % version
    print ''
    print 'This is a utility that writes the \'infinidb\' inventory file.  There'
    print 'are two ways to use it.  Either a file name needs to be specified via'
    print 'the --json option, or the -i option can be used to read the JSON'
    print 'from STDIN'
    print ''
    print '    -h            show help'
    print '    -v            print version'
    print '    -i            read ConsoleCmd from STDIN'
    print ''
    print '    --json <file> read ConsoleCmd from <file>'

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
        
    if (use_stdin and json_file) or (not use_stdin and not json_file):
        print 'ERROR: Must specify exactly one of -i or --json'
        usage()
        sys.exit(2)
        
    jsonstr = None
    if use_stdin:
        lines = sys.stdin.readlines()
        jsonstr = ''.join(lines)
    elif json_file:
        f = open( json_file )
        lines = f.readlines()
        jsonstr = ''.join(lines)
    
    # debug only
    # print '%s' % req
    try:
        req = inventoryreq.InventoryRequest( jsonstr )

        Log = logutils.getLogger('writeinventory')
        Log.info('request: %s' % req.json_dumps())

        pmgr = PlaybookMgr( req['cluster_name'] )
        
        # the write_inventory method expects a list for each role
        role_map = {}
        for r in req['role_info'].iterkeys():
            if type( req['role_info'][r] ) == list:
                role_map[r] = req['role_info'][r]
            elif type( req['role_info'][r] ) == unicode:
                role_map[r] = [ req['role_info'][r] ]
            else:
                raise Exception("writeinventory ERROR: unsupported type in role info %s : %s" % r, req['role_info'][r])
            
        pmgr.write_inventory('infinidb', role_map )
    except:
        import traceback
        print errormsg.ErrorMsg_from_parms( msg=json.dumps( traceback.format_exc() ) )
        sys.exit(1)

    reply_json = '{ "rc" : 0 }'
    Log.info('reply: %s' % reply_json)
    print reply_json
    return 0
    
#-------------------------------------------------------------------------------
# main entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
