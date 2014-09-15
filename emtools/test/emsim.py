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
getfacts.py

Accepts a FactRequest message as input and produces a FactReply
'''
import getopt
import os, sys

from emtools.playbookmgr import PlaybookMgr
import emtools.msg.factreq as factreq
import emtools.msg.factreply as factreply
import emtools.msg.errormsg as errormsg
import emtools.idbxml as idbxml
import json
import socket
import emtools.common.logutils as logutils
from emtools.common.utils import syscall_log

# roll this version for any significant changes
version = '0.1'
        
#-------------------------------------------------------------------------------
def usage():
    '''
    Print command line usage
    '''

    print 'emsim.py [hiv] [--hosts=,--roles=] <cluster_name> <ssh_user> <ssh_keyfile>'
    print ''
    print 'Version: %s' % version
    print ''
    print 'This is a test program that mimics the calls the EM server would'
    print 'make to emtools for a cluster'
    print ''
    print '    [Required]'
    print '    --hosts=<host1>,<host2>,...<hostn>'
    print '                  list of hosts to use for the cluster'
    print ''
    print '    [Optional]'
    print '    --roles=\'{ <role_dict> }\''
    print '                  dictionary with role mapping - required with more than one hostname'
    print '    --idbversion=<version>'
    print '                  InfiniDB package version - required when doing install'
    print '    --storagetype=[local|hdfs|gluster]'
    print '                  Storage type for install - defaults to local'
    print '    -h            show help'
    print '    -i            install infinidb (instead of installing EM)'
    print '    -v            print version'

def do_facts(cname,hostnames,keystr,ssh_user,requireInfinidb):
    factreq = {
        "cluster_name" : cname,
        "hostnames" : hostnames,
        "ssh_key" : keystr,
        "ssh_user" : ssh_user
    }
    
    frfile = '/tmp/factreq.json'
    wf = open(frfile,"w")
    wf.write(json.dumps(factreq))
    wf.close()
    cmd = 'getfacts.py --json %s' % frfile
    rc, out, err = syscall_log(cmd)
    
    if rc != 0:
        print 'ERROR: getfacts.py failed with return code %s!' % rc
        print 'stdout = %s' % out
        print 'stderr = %s' % err
        sys.exit(1)
    
    factreply = json.loads(out)
    if (not factreply['cluster_info']['valid']):
        print "ERROR: getfacts.py failed to detect a valid cluster:"
        print json.dumps(factreply, sort_keys=True, indent=4)
        sys.exit(1)
    elif (requireInfinidb and not factreply['cluster_info']['infinidb_version']):
        print "ERROR: emsim.py is not going to install InfiniDB, but an InfiniDB installation was not found, consider using -i:"
        sys.exit(1)
    else:
        print 'INFO: getfacts.py PASSED!'

    return factreply
    
def do_inv(cname, role_out):
    writeinv = {
        'cluster_name' : cname,
        'role_info' : role_out 
    }

    frfile = '/tmp/writeinv.json'
    wf = open(frfile,"w")
    wf.write(json.dumps(writeinv))
    wf.close()
    cmd = 'writeinventory.py --json %s' % frfile
    rc, out, err = syscall_log(cmd)
    
    if rc != 0:
        print 'ERROR: writeinventory.py failed with return code %s!' % rc
        print 'stdout = %s' % out
        print 'stderr = %s' % err
        return rc
    
    invreply = json.loads(out)
    if invreply['rc'] == 0:
        print 'INFO: writeinventory.py PASSED!'
    else:
        print "INFO: writeinventory.py FAILED:"
        print json.dumps(invreply, sort_keys=True, indent=4)
        
    return invreply['rc']
        
    
def do_console( cname, command):
    statreq = {
        'cluster_name' : cname,
        'command' : command,
    }

    statfile = '/tmp/status.json'
    wf = open(statfile,"w")
    wf.write(json.dumps(statreq))
    wf.close()
    cmd = 'idbconsole.py --json %s' % statfile
    rc, out, err = syscall_log(cmd)
    
    if rc != 0:
        print 'ERROR: idbconsole.py failed with return code %s!' % rc
        print 'stdout = %s' % out
        print 'stderr = %s' % err
        return rc
    
    statreply = json.loads(out)
    if statreply['rc'] == 0:
        print 'INFO: idbconsole.py %s PASSED!' % command
    else:
        print "INFO: idbconsole.py %s FAILED:" % command
        print json.dumps(statreply, sort_keys=True, indent=4)
        return statreply['rc']
    
    return 0

def do_playbook(cname,name,hostspec,extravars=''):
    pbreq = {
        'cluster_name' : cname,
        'playbook_info' : {
            'name' : name,
            'hostspec' : hostspec,
            'extravars' : extravars
        }
    }
        
    pbfile = '/tmp/playbook.json'
    wf = open(pbfile,"w")
    wf.write(json.dumps(pbreq))
    wf.close()
    cmd = 'runplaybook.py --json %s' % pbfile
    rc, out, err = syscall_log(cmd)
    
    if rc != 0:
        print 'ERROR: runplaybook.py failed with return code %s!' % rc
        print 'stdout = %s' % out
        print 'stderr = %s' % err
        return 1
    
    pbreply = json.loads(out)
    if pbreply['rc'] == 0:
        print 'INFO: runplaybook.py PASSED!'
    else:
        print "INFO: runplaybook.py FAILED:"
        print json.dumps(pbreply, sort_keys=True, indent=4)
        

    return pbreply['rc']
    
def do_config( cname, action, set_params=None, check_parm=None, check_val=None ):
    jsonreq = {
        'cluster_name' : cname,
        'action' : action,
    }
    if set_params:
        jsonreq['set_params'] = set_params

    jsonfile = '/tmp/config.json'
    wf = open(jsonfile,"w")
    wf.write(json.dumps(jsonreq))
    wf.close()
    cmd = 'config.py --json %s' % jsonfile
    rc, out, err = syscall_log(cmd)
    
    if rc != 0:
        print 'ERROR: config.py %s failed with return code %s!' % (action, rc)
        print 'stdout = %s' % out
        print 'stderr = %s' % err
        return rc
    
    jsonreply = json.loads(out)
    if jsonreply.has_key('failed') is False:
        print 'INFO: config.py %s PASSED!' % action
    else:
        print "INFO: config.py %s FAILED:" % action
        print json.dumps(jsonreply, sort_keys=True, indent=4)
        return jsonreply['rc']

    if action == 'get' and check_parm and check_val:
        for p in jsonreply['config']:
            if p['em_parameter'] == check_parm:
                if p['value'] == check_val:
                    print 'INFO: config.py chetk for %s==%s PASSED!' % (check_parm, check_val)
                    return 0
                else:
                    print 'ERROR: config.py chetk for %s==%s FAILED!' % (check_parm, check_val)
                    return 1
        print 'ERROR: config.py chetk for %s==%s FAILED, parm not found!' % (check_parm, check_val)
        return 1
                    
    return 0

def do_installdb(cname,hostnames,roles,idbversion,storage_type='local'):
    roleinfo = None
    if roles == None and len(hostnames) == 1:
        roleinfo = { 'pm1' : hostnames[0] }
    elif roles == None:
        print 'ERROR: do_installdb requires the roles map with more than 1 host!'
        return 1
    else:
        roleinfo = roles
        
    if idbversion == None:
        print 'ERROR: do_installdb requires idbversion be set!'
        return 1        
        
    installreq = {
        'cluster_name' : cname,
        'cluster_info' : {
            'infinidb_version' : idbversion,
            'dbroots_per_pm'   : 1,
            'infinidb_user'    : 'root',
            'storage_type'     : storage_type,
            'pm_query'         : False,
            'um_replication'   : False
        },
        'role_info' : roleinfo
    }

    installpb = '/tmp/installdb.json'
    wf = open(installpb,"w")
    wf.write(json.dumps(installreq))
    wf.close()
    cmd = 'installdatabase.py --json %s' % installpb
    rc, out, err = syscall_log(cmd)

    if rc != 0:
        print 'ERROR: installdatabase.py failed with return code %s!' % rc
        print 'stdout = %s' % out
        print 'stderr = %s' % err
        return 1

    pbreply = json.loads(out)
    if pbreply['rc'] == 0:
        print 'INFO: installdatabase.py PASSED!'
    else:
        print "INFO: installdatabase.py FAILED:"
        print json.dumps(pbreply, sort_keys=True, indent=4)

    return pbreply['rc']

#-------------------------------------------------------------------------------
def main(argv):
    '''
    main function
    '''
    
    try:                                
        opts, args = getopt.getopt(argv, "hiv", ["hosts=","roles=","idbversion=","storagetype="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)   
    
    # defaults
    installInfinidbFlag = False
    hostnames = []
    roles = None
    idbversion = None
    storage_type = None
    
    for o,a in opts:
        if o == '-h':
            usage()
            sys.exit(2)
        if o == '-i':
            installInfinidbFlag = True;
        elif o == '-v':
            print 'emsim.py Version: %s' % version
            sys.exit(1)
        elif o == '--hosts':
            hostnames = a.split(',')
        elif o == '--roles':
            roles = eval(a)
        elif o == '--idbversion':
            idbversion = a
        elif o == '--storagetype':
            storage_type = a
        else:
            print 'unsupported option: %s' % o
            usage()
            sys.exit(2)
        
    Log = logutils.getLogger('emsim')

    if len(args) < 3:
        print 'ERROR: Not enough command-line arguments!'
        usage()
        sys.exit(2)
    elif len(hostnames) < 1:
        print 'ERROR: Must specify at least one hostname with --hosts!'
        usage()
        sys.exit(2)
        
    cluster_name = args[0]
    ssh_user = args[1]
    ssh_keyfile = args[2]

    f = open(ssh_keyfile)
    keystr = ''.join(f.readlines())
    f.close()

    requireInfinidb = True
    if installInfinidbFlag:
        requireInfinidb = False
    factreply = do_facts(cluster_name, hostnames, keystr, ssh_user, requireInfinidb)

    # Install infinidb if user requested.
    if installInfinidbFlag:
        if do_installdb(cluster_name, hostnames, roles, idbversion, storage_type=storage_type) != 0:
            sys.exit(1)

        # run getfacts to verify the infinidb install
        factreply = do_facts(cluster_name, hostnames, keystr, ssh_user, True)

    # construct contents of inventory file from getfacts reply
    role_in = factreply['role_info']
    role_out = { "pm:children" : [] }
    for r in role_in:
        role_out[r] = [ role_in[r] ]
        role_out['pm:children'].append(r)
    if role_in.has_key('um1'):
        role_out['oam_server'] = role_in['um1']
    else:
        role_out['oam_server'] = role_in['pm1']

    if do_inv(cluster_name,role_out) != 0:
        sys.exit(1)

    # Install EM if user did not request alternate infinidb install
    if not installInfinidbFlag:
        if do_playbook(cluster_name, 'all.yml', 'all') != 0:
            sys.exit(1)

    if do_console(cluster_name, 'getsystemstatus') != 0:
        sys.exit(1)
    if do_console(cluster_name, 'getactivealarms') != 0:
        sys.exit(1)
    if do_console(cluster_name, 'gettablelocks') != 0:
        sys.exit(1)
        
    if do_config(cluster_name, 'set', set_params=[ { "em_category" : "UM", "em_parameter" : "TotalUmMemory", "value" : "1G" } ]) != 0:
        sys.exit(1)
    if do_config(cluster_name, 'get', check_parm="TotalUmMemory", check_val="1G") != 0:
        sys.exit(1)
    if do_config(cluster_name, 'set', set_params=[ { "em_category" : "UM", "em_parameter" : "TotalUmMemory", "value" : "4G" } ]) != 0:
        sys.exit(1)
    if do_config(cluster_name, 'get', check_parm="TotalUmMemory", check_val="4G") != 0:
        sys.exit(1)
        
    return 0
    
#-------------------------------------------------------------------------------
# main entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
