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
installdatabase.py

Performs an install of InfiniDB to the cluster / roles defined
'''
import getopt
import sys
import os

import emtools.msg.installreq as installreq
import emtools.msg.playbookreply as playbookreply
from emtools.cluster.configspec import ConfigSpec
from emtools.cluster.emcluster  import EmCluster
from emtools.cluster.emversionmgr import EmVersionManager
from emtools.cluster.postcfg import PostConfigureHelper
from emtools.common.utils import mkdir_p
import emtools.msg.errormsg as errormsg
import json
import emtools.common.logutils as logutils
import emtools.common as common

# roll this version for any significant changes
version = '0.1'

#-------------------------------------------------------------------------------
class ConfigSpecBuilder(object):
    def __init__(self, req):
        """Constructor"""
        self.__req = req

    def run(self):
        """Convert EM db installreq json string to a configspec"""

        # direct mapping of installreq properties to configspec properties
        # em db install properties      --> configspec properties
        # ------------------------          ---------------------
        #  cluster_name                     name
        #  cluster_info.infinidb_version    idbversion
        #  cluster_info.dbroots_per_pm      rolespec.pm.dbroots_per
        #  cluster_info.dbroot_list         rolespec.pm.dbroots_list
        #    (for future use)
        #  cluster_info.infinidb_user       idbuser
        #  cluster_info.storage_type
        #    "local"
        #    "gluster"                      datdup set to True
        #    "hdfs"                         empty hadoop entry
        #  cluster_info.pm_query            pm_query
        #  cluster_info.um_replication      Not Supported
        #  role_info                        rolespec.pm.count
        #
        # configspec properties that are constant or not applicable
        # ---------------------------------------------------------
        #  storage                          "internal"
        #  binary                           True
        #  upgrade                          False
        #  enterprise                       True
        #  hadoop.version                   not used (uses default)
        #  boxtype                          N/A
        #  em                               N/A
        #  rolespec.pm.memory               N/A
        #  rolespec.pm.cpus                 N/A

        cfgspec_dict = {}
        cfgspec_dict['name']       = self.__req['cluster_name']
        cfgspec_dict['idbversion'] = self.__req['cluster_info']['infinidb_version']
        cfgspec_dict['idbuser']    = self.__req['cluster_info']['infinidb_user']
        if self.__req['cluster_info']['storage_type'] == 'gluster':
            cfgspec_dict['datdup'] = True
        else:
            cfgspec_dict['datdup'] = False
        cfgspec_dict['binary']     = True
        cfgspec_dict['storage']    = 'internal'
        cfgspec_dict['upgrade']    = False
        cfgspec_dict['enterprise'] = True
        cfgspec_dict['pm_query']   = self.__req['cluster_info']['pm_query']
        if self.__req['cluster_info']['storage_type'] == 'hdfs':
            cfgspec_dict['hadoop'] = { } # use hadoop defaults
            cfgspec_dict['storage']    = 'hdfs'

        pmCount = 0
        umCount = 0;
        cfgspec_dict['rolespec'] = {}
        machines = {}
        dbroots_per_pm = self.__req['cluster_info']['dbroots_per_pm']
        for key in self.__req['role_info']:
            if key.startswith('pm'):
                pmCount += 1
                m = {}
                m['ip']       = self.__req['role_info'][key]
                m['hostname'] = self.__req['role_info'][key]
                dbroots = []
                pmnum = eval(key[2:])
                for j in range(1, dbroots_per_pm + 1):
                    dbroots.append(j+((pmnum - 1) * dbroots_per_pm))
                m['dbroots']  = dbroots
                machines[key] = m
            if key.startswith('um'):
                umCount += 1
                m = {}
                m['ip']       = self.__req['role_info'][key]
                m['hostname'] = self.__req['role_info'][key]
                machines[key] = m
        if pmCount > 0:
            cfgspec_dict['rolespec']['pm'] = {
                'count' : pmCount,
                'dbroots_per' : self.__req['cluster_info']['dbroots_per_pm'] }
        else:
            # throw exception if no PM's present
            pass
        if umCount > 0:
            cfgspec_dict['rolespec']['um'] = {
                'count' : umCount }

        cfgspec_json = json.dumps( cfgspec_dict )
        machines_json = json.dumps( machines )
        Log = logutils.getLogger('installdatabase')
        Log.info('configspec: %s' % cfgspec_json)
        Log.info('machines: %s' % machines_json)
        cfg = ConfigSpec(cfgspec_json)

        cfg.validate()

        return cfg,machines

#-------------------------------------------------------------------------------
def usage():
    '''
    Print command line usage
    '''

    print 'installdatabase.py [hvi] [--json=]'
    print ''
    print 'Version: %s' % version
    print ''
    print 'This utility installs an infinidb database as defined in the specified'
    print 'json file.  The json input can be specified in a file via the --json option,'
    print 'or by STDIN, through the -i option'
    print ''
    print '    -h            show help'
    print '    -v            print version'
    print '    -i            read installdatabase input from STDIN'
    print ''
    print '    --json <file> read installdatabase input from <file>'

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

    # parse command line arguments
    for o,a in opts:
        if o == '-h':
            usage()
            sys.exit(2)
        elif o == '-v':
            print 'installdatabase.py Version: %s' % version
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

    try:
        # load input into json string
        jsonstr = None
        if use_stdin:
            lines = sys.stdin.readlines()
            jsonstr = ''.join(lines)
        elif json_file:
            f = open( json_file )
            lines = f.readlines()
            jsonstr = ''.join(lines)

        Log = logutils.getLogger('installdatabase')
        req = installreq.InstallReq( jsonstr )
        Log.info('request: %s' % req.json_dumps())

        # construct configspec
        cfgspecbld = ConfigSpecBuilder( req )
        cfgspec,machines = cfgspecbld.run()

        # determine the approprate package file to be installed
        emVM = EmVersionManager()
        pkgfile = emVM.retrieve(cfgspec['idbversion'],'binary')
        Log.info('pkgfile: %s' % pkgfile)

        # create runtime directory
        root = common.props['emtools.playbookmgr.cluster_base']
        rundir = '%s/%s' % (root, cfgspec['name'])
        if not os.path.exists( rundir ):
            mkdir_p( rundir )

        # create the cluster
        emCluster = EmCluster(cfgspec['name'],
                              cfgspec,
                              rundir,
                              pkgfile,
                              machines)

        # create the postconfig response file
        h = PostConfigureHelper()
        pfile = '%s/postconfigure.in' % rundir
        h.write_input(pfile, emCluster, 'binary')

        # perform the db install
        rc, results, out, err = emCluster.run_install_recipe()

        reply_dict = {
            'cluster_name' : cfgspec['name'],
            'playbook_info': {
                'name'     : emCluster.get_playbook_filename(),
                'hostspec' : emCluster.get_inventory_filename(),
                'extravars': emCluster.get_extra_vars()
            },
            'rc'           : rc,
            'stdout'       : out,
            'stderr'       : err,
            'recap_info'   : results
        }

        # test stub output
        #reply_dict = {
        #    'cluster_name' : cfgspec['name'],
        #    'playbook_info': {
        #        'name'     : 'test_name',
        #        'hostspec' : 'test_hostspec',
        #        'extravars': 'test_extravars'
        #    },
        #    'rc'           : 0,
        #    'stdout'       : 'test_stdout',
        #    'stderr'       : 'test_stderr',
        #}
        preply = playbookreply.PlaybookReply_from_dict(reply_dict)

        Log.info('reply: %s' % preply.json_dumps())
        print preply

        return 0

    except:
        import traceback
        print errormsg.ErrorMsg_from_parms( msg=json.dumps( traceback.format_exc() ) )
        sys.exit(1)

#-------------------------------------------------------------------------------
# main entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
