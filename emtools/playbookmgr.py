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
emtools.playbookmgr

Contains:
    class PlaybookMgr
'''
import os, sys
from ConfigParser import ConfigParser
import emtools.common.properties as properties
import emtools.common.logutils as logutils
from emtools.msg.errormsg import ErrorMsg_from_parms
import shutil
from emtools.common.utils import syscall_log,mkdir_p
import json
import re

Log = logutils.getLogger(__name__)

class PlaybookMgr(object):
    '''
    PlaybookMgr manages an Ansible playbook specific to installation, etc.
    of InfiniDB clusters (incl. InfiniDB Enterprise Manager).
    
    Note that all methods of PlaybookMgr are designed to be idempotent - 
    this means that the result of calling a method is the same regardless
    of whether it is the first time or any number of subsequent times.
    
    Further, the playbook itself is a file/directory hierarchy on disk and
    is therefore reusable across invocations of any PlaybookMgr client.
    
    The structure of the playbook is as follows:
    
    <name>/
        ansible.cfg      - ansible configuration file
        .ssh/            - sub-directory for ssh key
            private_key  - ssh key
        <inventory>      - [optional] from write_inventory() 
    '''

    def __init__(self, name, extra_playbook_dir=None):
        '''
        Constructor.
        
        :param name: name of the playbook.  This will be a sub-directory of
                     either the current directory (basedir=None) or the 
                     specified basedir.
        :param extra_playbook_dir: specify an additional parent directory
                     for the playbooks.  This directory will be copied into
                     place after the default directory is copied.
        '''
        self.__name = name

        self.__props = properties.Properties()
        basedir = self.__props['emtools.playbookmgr.cluster_base']
        if not os.path.exists( basedir ):
            mkdir_p( basedir )
        self.__rootdir = '%s/%s' % (basedir, name)
        
        try:
            # this update may fail if the user has messed up 
            # file permissions among other reasons
            srcroot = self.__props['emtools.playbookmgr.playbook_template']
            self.__update_playbook( srcroot, self.__rootdir )
        except IOError, e:
            datastructure = { "failed" : True, "msg" : 'While attempting playbook update...%s' % e }
            print json.dumps(datastructure)
            sys.exit(1)

        if extra_playbook_dir != None:
            try:
                # this update may fail if the user has messed up
                # file permissions among other reasons
                self.__update_playbook( extra_playbook_dir, self.__rootdir )
            except IOError, e:
                datastructure = { "failed" : True, "msg" : 'While attempting extra playbook update...%s' % e }
                print json.dumps(datastructure)
                sys.exit(1)
            
        self.__configfile = '%s/ansible.cfg' % ( self.__rootdir )
        self.__config = ConfigParser()
        if os.path.exists( self.__configfile ):
            self.__config.read( self.__configfile )
            self.__read_config()
        
    def get_rootdir(self):
        '''Returns the playbook root directory.'''
        return self.__rootdir
    
    def run_module(self, inventory_file, host_pattern, module_name, module_args='', no_raise=False, sudo=False):
        '''
        Runs an ansible module.
        
        :param inventory_file: inventory file to use.
        :param host_pattern: pattern to use to select hosts (i.e. 'all').
        :param module_name: module name to run.
        :param module_args: module argument string.
        :param no_raise: do not do any error checking of the ansible result
        '''
        cwd = os.getcwd()
        os.chdir( self.__rootdir )
        
        tmpfile = '/tmp/%d.json' % os.getpid()
        cmd = "ansible -i %s '%s' -m %s -j %s" % (inventory_file, host_pattern, module_name, tmpfile)
        if module_args:
            cmd = cmd + " --args='%s'" % module_args
        if sudo:
            cmd = cmd + " -s"
            
        # make sure we don't have an old out.json
        if os.path.exists(tmpfile):
            os.remove(tmpfile)
        rc, out, err = syscall_log(cmd)
        if not os.path.exists(tmpfile):
            reslt = ErrorMsg_from_parms("no json output from ansible - likely no hosts matched host_pattern", 
                                        cmd, rc=rc, stdout=out, stderr=err)
            if not no_raise:
                raise reslt
            else:
                return reslt
        else:
            f = open(tmpfile)
            reslt = json.load(f)
            f.close()
            os.remove(tmpfile)
        
        os.chdir(cwd)

        if not no_raise:
            if reslt.has_key('failed'):
                raise ErrorMsg_from_parms(msg='run_module failure: %s' % ( reslt['msg'] ), 
                                          cmd=cmd, rc=rc, stdout=out, stderr=err)
            elif len(reslt['dark']):
                dark_host = reslt['dark'].keys()[0]
                if reslt['dark'][dark_host].has_key('msg'):
                    msg = 'dark host %s: %s' % (reslt['dark'].keys()[0], reslt['dark'][dark_host]['msg'])
                else:
                    # don't know if this is a real case or not
                    msg = 'dark host %s: %s' % (reslt['dark'].keys()[0], reslt['dark'])
                    
                raise ErrorMsg_from_parms(msg=msg, cmd=cmd, rc=rc, stdout=out, stderr=err)
            elif len(reslt['contacted']) >= 1:
                contacted = reslt['contacted'].keys()[0]
                if reslt['contacted'][contacted].has_key('failed'):
                    raise ErrorMsg_from_parms(msg='run_module failure: %s' % reslt['contacted'][contacted]['msg'],
                                              cmd='%s' % reslt['contacted'][contacted]['cmd'],
                                              rc=rc, stdout=out, stderr=err)
                elif reslt['contacted'][contacted].has_key('rc') and reslt['contacted'][contacted]['rc'] != 0:
                    raise ErrorMsg_from_parms(msg='run_module failure: %s' % 'see stdout/stderr',
                                              cmd='%s' % reslt['contacted'][contacted]['cmd'],
                                              rc=rc, stdout=out, stderr=err)
            else:
                raise ErrorMsg_from_parms(msg="Unknown error, no dark or contacted hosts in %s..." % reslt,
                                          cmd=cmd, rc=rc, stdout=out, stderr=err)

        return reslt
           
    def run_playbook(self, playbook_file, inventory_file, host_subset=None, playbook_args=None):
        '''
        Runs an ansible playbook.
        
        :param playbook_file: playbook YAML file
        :param inventory_file: inventory file to use
        :param host_subset: list of hosts to receive the playbook
        :param playbook_args: quoted string passed to playbook as extra-vars argument
        '''
        cwd = os.getcwd()
        os.chdir( self.__rootdir )

        cmd = "ansible-playbook -i %s %s" % (inventory_file, playbook_file)
        if host_subset:
            cmd = cmd + " -l '%s'" % host_subset
        if playbook_args:
            cmd = cmd + " --extra-vars=%s" % playbook_args
        rc, out, err = syscall_log(cmd)
        recap_section = False
        results = {}
        patt = re.compile('([a-zA-Z0-9\-_\.]+)\s+:\s+ok=([0-9]+)\s+changed=([0-9]+)\s+unreachable=([0-9]+)\s+failed=([0-9]+)')
        for l in out.split('\n'):
            if recap_section:
                mat = patt.match(l)
                if mat:
                    results[mat.group(1)] = {
                        "ok" : int(mat.group(2)),
                        "changed" : int(mat.group(3)),
                        "unreachable" : int(mat.group(4)),
                        "failed" : int(mat.group(5))
                    }
            elif l.find('PLAY RECAP') == 0:
                recap_section = True

        os.chdir(cwd)
        return rc, results, out, err
             
    def write_vars(self, group_name, varlist):
        '''
        Creates a new variables file under the playbook
        group_vars/ directory
        
        :param group_name: variables file name to create
        :param varlist: list of (name, value) pairs
        '''
        varfile = '%s/group_vars/%s.yml' % ( self.__rootdir, group_name )
        wf = open( varfile, 'w' )
        wf.write('---\n')
        wf.write('# file: group_vars/%s.yml\n' % group_name)
        for var in varlist:
            wf.write('%s: %s\n' % (var[0],var[1]))
        wf.close()
        
    def write_inventory(self, file_, invdict):
        '''
        Creates a new Ansible inventory file.  The inventory file
        will be created in the root directory of the playbook.  Note
        that write_inventory overwrites any prior inventory file of 
        the same name.
        
        :param file_: file name to create.
        :param invdict: dictionory containing inventory contents.  Each
                        key is a group in the file.  Each value should
                        be a list of the hostnames in that group.
        '''
        invfile = '%s/%s' % ( self.__rootdir, file_ )
        
        wf = open( invfile, 'w' )
        for group in invdict.iterkeys():
            wf.write( '[%s]\n' % group)
            
            for h in invdict[group]:
                wf.write( '%s\n' % h )
                
        wf.close()
    
    def read_inventory(self, inventory):
        '''
        Read inventory file in the root directory of the playbook.
         
        :param inventory: file name to read.
        return dictionory containing inventory contents.  
        '''
        cur_section = 'root'
        ret = { 'root' : [] }
        #print self.__rootdir+'/'+inventory
       
        f = open(self.__rootdir+'/'+inventory)
        for l in f.readlines():
            l = l.strip()
            if len(l):
                if l[0] == '[':
                    cur_section = l[1:len(l)-1]
                    ret[cur_section] = []
                else:
                    ret[cur_section].append( l )
        f.close()
        return ret

    
    def config_ssh(self, ssh_user, ssh_key=None, ssh_pass=None, ssh_port=None):
        '''
        Configures ssh access for the playbook.  This method will write
        a .ssh/private_key inside the root playbook directory and also
        create ond/or update an ansible.cfg file with corresponding settings.
        
        :param ssh_user: user to use when connecting over ssh
        :param ssh_key: ssh key text
        :param ssh_pass: ssh password
        :param ssh_part: [optional] override the default ssh part
        
        Notes:  exactly one of ssh_key and ssh_pass must be set
        '''
        # we'll need to update ansible.cfg so get a dictionary started
        cfgvars = { "remote_user" : ssh_user, 
                    "host_key_checking" : "False",
                    "log_path" : "./log/ansible.log" }
        
        if ssh_key:
            # this is an actual key - we need to write a key file
            sshdir = '%s/.ssh' % self.__rootdir
            if not os.path.exists( sshdir ):
                os.makedirs( sshdir )
            keyfile = '%s/private_key' % sshdir
            kf = open( keyfile, 'w' )
            kf.write( ssh_key )
            kf.close()
            os.chmod( keyfile, 0o600 )
            # we want this path to be relative to the base playbook directory
            cfgvars['private_key_file'] = './.ssh/private_key'
        elif ssh_pass:
            cfgvars['ssh_pass'] = ssh_pass
        else:
            raise Exception("ERROR-must specify one of ssh_key or ssh_pass to configure ssh")
            
        if ssh_port != None:
            cfgvars['remote_port'] = '%s' % ssh_port
        
        cfgvars['transport'] = 'ssh'
        self.__update_config( 'defaults', cfgvars )
        sshvars = {
            'pipelining' : 'True',
            'ssh_args' : ''
        }
        self.__update_config( 'ssh_connection', sshvars )
            
    def __read_config(self):
        '''
        Reads the current config and sets internal state variables.
        '''
        try:
            self.__remote_user = self.__config.get('defaults', 'remote_user')
        except:
            self.__remote_user = None
        try:
            self.__private_key_file = self.__config.get('defaults', 'private_key_file')
        except:
            self.__private_key_file = None
        try:
            self.__ssh_pass = self.__config.get('defaults', 'ssh_pass')
        except:
            self.__ssh_pass = None
        
    def __update_config(self, section, vars_):
        '''
        Updates settings in ansible.cfg.  Each playbook will have an
        ansible.cfg file in the root playbook directory (at least after
        a config_ssh()).  Note that this method uses append semantics - 
        Any value that existed prior to the call and unmodified will
        retain the same value.
        
        :param section: section name for the variables
        :param vars_: dictionary containing variable/value pairs to be
                      updated in the config file.
        '''
            
        if not self.__config.has_section( section ):
            self.__config.add_section( section )
            
        for v in vars_.iterkeys():
            self.__config.set( section, v, vars_[v] )
            
        wf = open( self.__configfile, 'w' )
        self.__config.write(wf)
        wf.close()
        self.__read_config()
        
    def __update_playbook(self, srcroot, rootdir):
        '''
        Updates a playbook from the current playbook template.
        
        :param srcroot: source root directory name for the playbook
        :param rootdir: destination directory name for the playbook
        '''

        destroot = rootdir
        
        if not os.path.isdir( destroot ):
            os.mkdir(destroot)

        # Create log directory for playbook
        # Ansible does not auto create the directory if missing
        logdir = destroot + '/log'
        if not os.path.isdir( logdir ):
            os.mkdir(logdir)
        
        # uni-directional copy from source to dest
        starting = srcroot
        for dirname, dirnames, filenames in os.walk(starting):
            
            # because we used an absolute path to walk we have to strip off
            # the start path so that we can use it to build a local reference path
            dirname = dirname.replace('%s' % srcroot,'')
            if dirname.find('/') == 0:
                dirname = dirname[1:]
                
            for filename in filenames:
                # want to skip ansible.log - it is in the repo only to make the
                # log directory be created on a clone

                if filename != 'ansible.log':
                    src_file = os.path.join(srcroot, dirname, filename)
                    dest_file = os.path.join(destroot, dirname, filename)

                    if os.path.exists(dest_file) and not os.path.isfile(dest_file):
                        # this is odd.  There is a directory where there should be a file
                        shutil.rmtree(dest_file)

                    if not os.path.exists(dest_file) or (os.path.exists(dest_file) and
                         (os.path.getmtime(dest_file) != os.path.getmtime(src_file))):
                        shutil.copy2(src_file, dest_file)
                            
            for dir in dirnames:
                src_dir = os.path.join(srcroot, dirname, dir)
                dest_dir = os.path.join(destroot, dirname, dir)
 
                if os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
                    # this is odd.  there is a file where there should be a directory
                    shutil.rmtree(dest_dir)
               
                if not os.path.exists(dest_dir):
                    shutil.copytree(src_dir, dest_dir)
