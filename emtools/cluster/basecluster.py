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
emtools.cluster.basecluster

Base class to represent a group of machine instances that form a cluster
'''
import os
from abc import abstractmethod
from playbookinstall import PlaybookInstall
import emtools.common.logutils as logutils
import emtools.common as common
import emtools.common.utils as utils

Log = logutils.getLogger(__name__)

class BaseCluster(object):

    def __init__(self, name, configspec, machines = None, chefmode = True):
        '''Constructor.
        
        @param name - name for the cluster (ideally unique)
        @param configspec - reference to a ConfigSpec object
        @param machines - [optional] map with instantiated machine info
        '''
        if machines == None:
            machines = {}
        self._name = name
        self._config = configspec
        self._machines = machines
        self._chefmode = chefmode

    def name(self):
        """Returns the cluster instance name."""
        return self._name
        
    def id(self):
        """Returns the id."""
        return ""
    
    def config(self):
        """Returns the ConfigSpec instance."""
        return self._config

    def emapi(self):
        """Returns the EnterpriseManagerAPI instance."""
        return None
    
    def chefmode(self):
        """Returns true if using chef to generate cluster; false if using ansible"""
        return self._chefmode
    
    def add_machine(self, name, machine):
        """Adds a new machine to the cluster."""
        self._machines[name] = machine

    def role_alias(self, name):
        # if this is a cluster with combo-nodes there will not be an um roles
        # but we still want to support access to machines through um aliases
        if not self._config['rolespec'].has_key('um'):
            if name[0:2] == 'um':
                name = 'pm' + name[2:]
        return name
        
    def machine(self, name):
        """Returns a specific machine."""
        name = self.role_alias(name)
                
        if not self._machines.has_key(name):
            raise ValueError("Machine name %s not in %s" % (name, self._machines.keys()))
        
        return self._machines[name]

    def machines(self):
        """Returns the machines dictionary."""
        return self._machines
    
    #TBD: vmi vmi() stub
    def vmi(self, vmi):
        """Sets the VMI instance."""
        return
        
    #TBD: vmi get_vmi() stub
    def get_vmi(self):
        """Returns the VMI instance."""
        return None

    #TBD: vmi get_pkgfile() stub
    def get_pkgfile(self):
        """Returns pkg file name"""
        return ""

    #TBD: vmi get_rundir() stub
    def get_rundir(self):
        """Returns runtime directory"""
        return ""

    #TBD: vmi get_upgfile() stub
    def get_upgfile(self):
        """Returns upgrade pkg file name"""
        return ""

    def get_pkgdir(self):
        """Returns cache package directory"""
        return ""

    def get_extra_playbook_dir(self):
        """Returns extra playbook template directory"""
        return None

    def get_sshkey_text(self):
        """Returns sshkey text (to be stored in ansible.cfg)"""
        return ""

    def get_postconfig_opts(self):
        """Returns cmd line options to be passed to postConfigure"""
        return ""
    
    #TBD: vmi jsonmap() stub
    def jsonmap(self):
        """Returns a JSON encoding of the entire cluster."""
        return None
    
    #TBD: vmi status() stub
    def status(self):
        """Returns an aggregate status of the cluster.
        
        Return value is one of:
            'not created'       : cluster vms not created, pending call to 'vagrant up'
            'poweroff'          : cluster vms created, but all powered off
            'partially created' : some vms created, some not - possible if there is an in progress 'vagrant up'
            'partially up'      : all vms created, some up, some not - could be interim startup state or intentional during test execution
            'running'           : all vms running
        """
        return None
        
    #TBD: vmi start() stub
    def start(self):
        """Starts the cluster initially.  This method is intended to be called only once"""
        return 0

    #TBD: vmi poweron() stub
    def poweron(self, role=None):
        """Power on one or more nodes.  If role=None, then all power on"""
        return 0

    #TBD: vmi poweroff() stub
    def poweroff(self, role=None):
        """Power off one or more nodes.  If role=None, then all power off"""
        return 0

    #TBD: vmi pause() stub
    def pause(self):
        """Pause the cluster (saves state and stops)"""
        return 0

    #TBD: vmi resume() stub
    def resume(self):
        """Resume the cluster after a pause"""
        return 0

    #TBD: vmi destroy() stub
    def destroy(self):
        """Destroys the cluster and all file system artifacts related to the cluster.  DESTRUCTIVE operation."""
        return 0

    #TBD: vmi destroy_files_only() stub
    def destroy_files_only(self):
        """Destroys local file system artifacts only; useful in cleaning up unit tests.  DESTRUCTIVE operation."""
        return 0

    #TBD: vmi shell_command() stub
    def shell_command(self, role, cmd, calpontbin=False, polling=False, timeout=-1):
        """Runs a shell commnd on the specified cluster node using ssh."""
        return 0
        
    def calpont_console_cmd(self, cmd):
        """Issues a calpont console command on pm1."""
        cmd_ = '%s/bin/calpontConsole %s' % (self._config.infinidb_install_dir(), cmd)
        return self.shell_command('pm1', cmd_)

    @abstractmethod
    def run_install_recipe(self):
        """Run the proper install recipe."""

    @abstractmethod
    def run_upgrade_recipe(self):
        """Run the proper upgrade recipe."""
