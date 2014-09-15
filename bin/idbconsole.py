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
idbconsole.py

Runs a calpontConsole command on an InfinidB cluster and returns JSON result
'''
import getopt
import os, sys

from emtools.playbookmgr import PlaybookMgr
import emtools.msg.commandreq as commandreq
import emtools.msg.commandreply as commandreply
import emtools.msg.errormsg as errormsg
import json
import re
import emtools.cluster.console as console
import emtools.common.logutils as logutils

# roll this version for any significant changes
version = '0.1'

class ConsoleRunner(object):
    def __init__(self, cmd):
        self.__cmd = cmd
        self.__pmgr = PlaybookMgr( cmd['cluster_name'] )
        
    def run(self):
        
        cmdstr = ''
        if self.__cmd['command'] == 'gettablelocks':
            cmdstr = cmdstr + '{{ infinidb_installdir }}/bin/viewtablelock'
        else:
            cmdstr = cmdstr + '{{ infinidb_installdir }}/bin/calpontConsole %s' % self.__cmd['command']
        
        try:
            reslt = self.__pmgr.run_module( 'infinidb', 'pm1', 'command', cmdstr, sudo=False)
        except errormsg.ErrorMsg, exc:
            replydict = {
                "cluster_name" : self.__cmd['cluster_name'],
                "command" : self.__cmd['command'],
                "console_host" : '',
                "rc" : exc['rc'],
                "stdout" : exc['stdout'],
                "stderr" : exc['stderr'],
                "msg"    : exc['msg'],
                "ansible_cmd" : exc['cmd']
                }

            return commandreply.CommandReply_from_dict( replydict )
        
        host = reslt['contacted'].keys()[0]
        replydict = {
            "cluster_name" : self.__cmd['cluster_name'],
            "command" : self.__cmd['command'],
            "console_host" : host,
            "rc" : reslt['contacted'][host]['rc'],
            "stdout" : reslt['contacted'][host]['stdout'],
            "stderr" : reslt['contacted'][host]['stderr']
            }
        
        try:
            fn = getattr(console,self.__cmd['command'])
            replydict['results'] = fn(reslt['contacted'][host]['stdout'])
        except:
            pass
        
        return commandreply.CommandReply_from_dict( replydict )
    
        
#-------------------------------------------------------------------------------
def usage():
    '''
    Print command line usage
    '''

    print 'idbconsole.py [hvi] [--json=]'
    print ''
    print 'Version: %s' % version
    print ''
    print 'This is a utility that runs a calpontConsole command.  There are'
    print 'two ways to use it.  Either a file name needs to be specified via'
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
    
    cmd = commandreq.CommandReq( jsonstr )

    Log = logutils.getLogger('idbconsole')
    Log.info('request: %s' % cmd.json_dumps())
    
    # debug only
    # print '%s' % cmd
    
    runner = ConsoleRunner( cmd )
    reply = runner.run()
    
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
