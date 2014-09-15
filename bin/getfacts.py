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

# roll this version for any significant changes
version = '0.1'

class FactGetter(object):
    def __init__(self, req):
        self.__req = req
        
        self.__pmgr = PlaybookMgr( req['cluster_name'] )
        # TODO - add support for ssh_pass
        ssh_port = None
        if req.has_key('ssh_port'):
            ssh_port = req['ssh_port']
        if req.has_key('ssh_key'):
            self.__pmgr.config_ssh( req['ssh_user'], req['ssh_key'], ssh_port=ssh_port )
        else:
            self.__pmgr.config_ssh( req['ssh_user'], ssh_pass=req['ssh_pass'], ssh_port=ssh_port )
            
        self.__pmgr.write_inventory( 'default', { 'all' : req['hostnames'] })
        self.__role_info = {}
        self.__instance_info = {}
        self.__parsed_idbxml = False
        self.__user = req['ssh_user']

    def write_envsetup(self):
        fname = '%s/env-setup' % self.__pmgr.get_rootdir()
        f = open( fname, 'w' )
        f.write('#!/bin/bash\n')
        envvars = ['PYTHONPATH','ANSIBLE_LIBRARY','INFINIDB_EM_TOOLS_HOME']
        for var in envvars:
            if os.environ.has_key(var):
                f.write('export %s=%s\n' % (var, os.environ[var]))
                
    def run_host(self, hostname):
        # debug only
        #print 'Running host %s' % hostname
        
        reslt = self.__pmgr.run_module( 'default', hostname, 'setup', no_raise=True, sudo=False )
        
        fqdn = ''
        for h in reslt['dark']:
            fqdn = h
            self.__instance_info[fqdn] = dict( valid=False,
                                     reason=reslt['dark'][h]['msg'] )
        for h in reslt['contacted']:
            
            if reslt['contacted'][h].has_key('failed'):
                # module execution failed, we need to report the error
                self.__instance_info[h] = dict( valid=False,
                                         reason=reslt['contacted'][h]['msg'] )
            elif reslt['contacted'][h].has_key('ansible_facts'):
                host_facts = reslt['contacted'][h]['ansible_facts']
                fqdn = host_facts['ansible_fqdn']
                
                # do a test here to make sure that the server running emtools
                # can resolve the FQDN that ansible found.  This guards against
                # a local, unrouteable hostname.  Note that we already know the
                # original IP was ok because ansible was able to contact the host
                try:
                    # try a lookup
                    host = socket.gethostbyname(fqdn)
                except:
                    # this is bad - it means the hostname is non-routable from the server
                    self.__instance_info[fqdn] = dict( valid=False,
                                                    reason='non-routeable FQDN: %s' % h)
                    continue
                
                # we made contact so let's run our site_facts module
                try:
                    site_reslt = self.__pmgr.run_module( 'default', hostname, 'site_facts', sudo=False )
                except errormsg.ErrorMsg, exc:
                    self.__instance_info[h] = dict( valid=False,
                                                    reason=exc['msg'] )

                    continue

                site_facts = site_reslt['contacted'][h]['ansible_facts']

                self.__instance_info[fqdn] = dict()
                
                # this first group of checks will determine whether the node is valid from 
                # an EM perspective
                self.__instance_info[fqdn]['homedir'] = site_facts['homedir']                
                self.__instance_info[fqdn]['python_version'] = host_facts['ansible_python_version']
                self.__instance_info[fqdn]['sudo'] = site_facts['sudo']
                valid = True if ( self.__instance_info[fqdn]['sudo'] and
                                  ( self.__instance_info[fqdn]['python_version'][0:3] == '2.6' or 
                                    self.__instance_info[fqdn]['python_version'][0:3] == '2.7') ) else False
                self.__instance_info[fqdn]['valid'] = valid        
                if not valid:
                    reason = 'no posswardless sudo' if not self.__instance_info[fqdn]['sudo'] else 'unsupported python version'
                else:
                    reason = ''
                self.__instance_info[fqdn]['reason'] = reason
                
                self.__instance_info[fqdn]['ip_address'] = host_facts['ansible_all_ipv4_addresses'][0]
                self.__instance_info[fqdn]['hostname'] = host_facts['ansible_hostname']
                self.__instance_info[fqdn]['os_family'] = host_facts['ansible_distribution']                                
                self.__instance_info[fqdn]['gluster_version'] = site_facts['gluster_version']
                self.__instance_info[fqdn]['hadoop_version'] = site_facts['hadoop_version']
                self.__instance_info[fqdn]['pdsh_version'] = site_facts['pdsh_version']
                self.__instance_info[fqdn]['infinidb_version'] = site_facts['infinidb_version']
                self.__instance_info[fqdn]['infinidb_installdir'] = site_facts['infinidb_installdir']
                self.__instance_info[fqdn]['infinidb_user'] = site_facts['infinidb_user']
                # ansible does not report ansible_processor_vcpus on Mac OS
                if host_facts.has_key('ansible_processor_vcpus'):
                    self.__instance_info[fqdn]['processor_count'] = host_facts['ansible_processor_vcpus']
                else:
                    self.__instance_info[fqdn]['processor_count'] = host_facts['ansible_processor_cores']                    
                self.__instance_info[fqdn]['memory_available'] = host_facts['ansible_memtotal_mb']
                # ansible does not report ansible_swaptotal_mb on Mac OS
                if host_facts.has_key('ansible_swaptotal_mb'):
                    self.__instance_info[fqdn]['swap_configured'] = host_facts['ansible_swaptotal_mb']
                self.__instance_info[fqdn]['em_components'] = {}
                self.__instance_info[fqdn]['em_components']['collectd'] = site_facts['collectd_version']
                self.__instance_info[fqdn]['em_components']['python-stack'] = site_facts['python-stack_version']
                self.__instance_info[fqdn]['em_components']['graphite'] = site_facts['graphite_version']
                self.__instance_info[fqdn]['em_components']['tools'] = site_facts['tools_version']
                self.__instance_info[fqdn]['em_components']['oam-server'] = ''
                self.__instance_info[fqdn]['deployment_type'] = ''
                self.__instance_info[fqdn]['storage_type'] = ''
                self.__instance_info[fqdn]['system_name'] = ''
                self.__instance_info[fqdn]['port3306available'] = site_facts['port3306available']
            else:
                # no clue what happened - didn't see Failed but no ansible facts, return the whole result in the reason field
                self.__instance_info[h] = dict( valid=False,
                                         reason='%s' % reslt['contacted'][h] )

        if not self.__parsed_idbxml and self.__instance_info[fqdn]['valid'] and self.__instance_info[fqdn]['infinidb_version'] and self.__instance_info[fqdn]['sudo']:
            self.__parsed_idbxml = True
            # we found infinidb software.  Run our getinfo playbook to retrieve Calpont.xml
            rc, results, out, err = self.__pmgr.run_playbook('getinfo.yml', 'default', host_subset=hostname)
            if rc == 0:
                xml = idbxml.IdbXml( '%s/cluster_files/Calpont.xml' % (self.__pmgr.get_rootdir()) )
                for r in xml.get_all_roles():
                    # eoch role here has role= and ip_address= but we need to put
                    # map role to hostname for our reply.
                    role = r['role']
                    ip = r['ip_address']
                    for i in self.__instance_info.iterkeys():
                        self.__instance_info[i]['deployment_type'] = xml.get_parm('Installation', 'ServerTypeInstall')
                        self.__instance_info[i]['storage_type'] = xml.get_parm('Installation', 'DBRootStorageType')
                        self.__instance_info[i]['system_name'] = xml.get_parm('SystemConfig', 'SystemName')

                    host = ''
                    try:
                        # try a lookup
                        host = socket.gethostbyaddr(ip)[0]
                        if host == 'localhost':
                            host = fqdn
                    except:
                        # this is bad - it means that the Calpont.xml we found uses IP addresses that don't
                        # resolve to hostnames on the server.
                        self.__instance_info[fqdn]['valid'] = False
                        self.__instance_info[fqdn]['reason'] = 'Calpont.xml contained IP address %s that does not resolve to a hostname' % ip
                        break

                    self.__role_info[role] = host

                    # check to see if this host needs to be added to the request
                    if not self.__instance_info.has_key(host):
                        self.__req['hostnames'].append(host)
                        self.__pmgr.write_inventory( 'default', { 'all' : self.__req['hostnames'] })
                        self.run_host(host)
        
                if self.__instance_info[fqdn]['valid']:
                    # only do these updates if the node is still considered valid - may get set to False
                    # above if unknown IPs in Calpont.xml
                    invdict =  { 'all' : self.__req['hostnames'], 
                                 'pm:children' : [ 'pm1' ],
                                 'pm1' : [ self.__role_info['pm1'] ] }
                    if self.__role_info.has_key('pm2'):
                        invdict['pm2'] = [ self.__role_info['pm2'] ]
                    self.__pmgr.write_inventory( 'infinidb', invdict )
                    
                    varlist = [ ('em_server',socket.gethostbyname(socket.gethostname())),
                                ('infinidb_installdir',self.__instance_info[fqdn]['infinidb_installdir']),
                                ('infinidb_user',self.__instance_info[fqdn]['infinidb_user']) ]
                    self.__pmgr.write_vars('pm', varlist)
            else:
                # some kind of problem running getinfo.yml...Will reset the entire host info
                self.__instance_info[h] = {
                    'valid' : False,
                    'reason': 'Failed to run playbook getinfo.yml: rc=%s, stdout=%s, stderr=%s' % \
                                ( rc, out, err )
                }

    def run(self):
        cluster_valid = True
        cluster_dist = ''
        cluster_reason = ''
        valid_instances = 0
        cluster_gluster = ''
        cluster_hadoop = ''
        cluster_infinidb = ''
        cluster_infinidb_installdir = ''
        cluster_infinidb_user = ''
        cluster_storage_type = ''
        cluster_deployment_type = ''
        cluster_primary_um = 'None'
        cluster_primary_pm = ''
        cluster_secondary_pm = 'None'
        cluster_oam_server = ''
        cluster_name = ''
        cluster_homedir = ''
        cluster_port3306available = True
        
        for hostname in self.__req['hostnames']:
            if not self.__instance_info.has_key(hostname):
                self.run_host(hostname)

        for i in self.__instance_info.itervalues():
            
            if i['valid']:
                valid_instances = valid_instances + 1
            else:
                break
                             
            if not cluster_dist:
                cluster_dist = i['os_family']
            elif cluster_dist != i['os_family']:
                cluster_valid = False
                cluster_reason = 'Multiple distributions: %s and %s' % (cluster_dist, i['os_family']) 

            if not cluster_gluster and i['gluster_version']:
                cluster_gluster = i['gluster_version']

            if not cluster_hadoop and i['hadoop_version']:
                cluster_hadoop = i['hadoop_version']

            if not cluster_infinidb and i['infinidb_version']:
                cluster_infinidb = i['infinidb_version']
                cluster_infinidb_installdir = i['infinidb_installdir']
                cluster_infinidb_user=i['infinidb_user']
            
            if not cluster_deployment_type and i['deployment_type']:
                if i['deployment_type'] == '2':
                    cluster_deployment_type = 'Combined UM/PM'
                else:
                    cluster_deployment_type = 'Separate UM/PM'

            if not cluster_storage_type and i['storage_type']:
                cluster_storage_type = i['storage_type']

            if not cluster_name and i['system_name']:
                cluster_name = i['system_name']
                
            if not cluster_homedir and i['homedir']:
                cluster_homedir = i['homedir']
            elif cluster_homedir != i['homedir']:
                cluster_valid = False
                cluster_reason = 'Multiple home directories: %s and %s' % (cluster_homedir, i['homedir']) 
                
            if not i['port3306available']:
                cluster_port3306available = False
                
            
        if valid_instances == 0:
            cluster_valid = False
            cluster_reason = 'No valid hosts'
            
        if not cluster_infinidb and cluster_valid:
            # we didn't find InfiniDB so we will populate installdir and user 
            # with what the values would need to be for install.
            cluster_infinidb_installdir = '/usr/local/Calpont' if ( self.__user == 'root' ) else '%s/Calpont' % cluster_homedir
            cluster_infinidb_user = self.__user
            
        if self.__role_info.has_key('pm1'):
            cluster_primary_pm = self.__role_info['pm1']
        if self.__role_info.has_key('pm2'):
            cluster_secondary_pm = self.__role_info['pm2']
        if self.__role_info.has_key('um1'):
            cluster_primary_um = self.__role_info['um1']
            
        cluster_info = dict(
            valid=cluster_valid,
            name=cluster_name,
            os_family=cluster_dist,
            reason=cluster_reason,
            gluster_version=cluster_gluster,
            hadoop_version=cluster_hadoop,
            infinidb_version=cluster_infinidb,
            infinidb_installdir=cluster_infinidb_installdir,
            infinidb_user=cluster_infinidb_user,
            em_version='1.0',
            storage_type=cluster_storage_type,
            deployment_type=cluster_deployment_type,
            primary_um=cluster_primary_um,
            primary_pm=cluster_primary_pm,
            secondary_pm=cluster_secondary_pm,
            oam_server=cluster_oam_server,
            port3306available=cluster_port3306available
            )
            
        if cluster_info['valid']:
            self.write_envsetup(
                                )
        reply = factreply.FactReply_from_dict( { "cluster_info" : cluster_info, "instance_info" : self.__instance_info, "role_info": self.__role_info})
        return reply
        
        
#-------------------------------------------------------------------------------
def usage():
    '''
    Print command line usage
    '''

    print 'getfacts.py [hvik:] [--json=]'
    print ''
    print 'Version: %s' % version
    print ''
    print 'This is a utility that performs the get facts use case.  There are'
    print 'two ways to use it.  Either a file name needs to be specified via'
    print 'the --json option, or the -i option can be used to read the JSON'
    print 'from STDIN'
    print ''
    print '    -h            show help'
    print '    -v            print version'
    print '    -i            read FactRequest from STDIN'
    print '    -k <file>     prints a JSON-friendly version of the ssh private' 
    print '                  key file <file> for inclusion into a FactRequet'
    print ''
    print '    --json <file> read FactRequest from <file>'

#-------------------------------------------------------------------------------
def main(argv):
    '''
    main function
    '''
    
    try:                                
        opts, args = getopt.getopt(argv, "hvik:", ['json='])
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
        elif o == '-k':
            f = open(a)
            keystr = ''.join(f.readlines())
            print json.dumps(keystr)
            sys.exit(0)
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

    Log = logutils.getLogger('getfacts')
    req = factreq.FactRequest( jsonstr )
    Log.info('request: %s' % req.json_dumps())
    
    # debug only
    # print '%s' % req
    
    fget = FactGetter( req )
    reply = fget.run()
    
    Log.info('reply: %s' % reply.json_dumps())
    print reply
    
    return 0
    
#-------------------------------------------------------------------------------
# main entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
