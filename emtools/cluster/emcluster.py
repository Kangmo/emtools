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
emtools.cluster.emcluster

Represent a group of machine instances that form a cluster
'''
import os
from playbookinstall import PlaybookInstall
import emtools.common.logutils as logutils
import emtools.common as common
import emtools.common.utils as utils
from emtools.cluster.basecluster import BaseCluster

Log = logutils.getLogger(__name__)

class EmCluster(BaseCluster):

    def __init__(self, name, configspec, rundir, pkgfile, machines = None, chefmode = True):
        '''Constructor.
        
        @param name - name for the cluster (ideally unique)
        @param configspec - reference to a ConfigSpec object
        @param rundir - runtime directory
        @param pkgfile - name of pkg file to be installed
        @param machines - [optional] map with instantiated machine info
        '''
        # Never employ chefmode for EmCluster
        super(EmCluster, self).__init__(name, configspec, machines=machines, chefmode=False)
        self._rundir  = rundir
        self._pkgfile = pkgfile
        self._ansible_file = ''
        self._extra_vars   = ''
        self._inventory_filename = ''
 
    #TBD: implement other base class function as needed:
    #   vmi, get_vmi, jsonmap, status, start, poweron, poweroff, pause
    #   resume, destroy, destroy_files_only, shell_command

    def run_install_recipe(self):
        """Run the proper install recipe."""
        Log.info('Performing InfiniDB install')
        recipe = 'binary_install'
        rc, results, out, err = self._run_ansible_playbook(recipe)
        if rc != 0:
            Log.error('There were errors installing InfiniDB')

        return rc, results, out, err
        
    def run_upgrade_recipe(self):
        """Run the proper upgrade recipe."""
        if not self.config()['upgrade']:
            Log.warn('No upgrade version specified in ConfigSpec!')
            return 1,None,"",""
        recipe = 'binary_upgrade'

        rc, results, out, err = self._run_ansible_playbook(recipe)
        if rc != 0:
            Log.error('There were errors upgrading InfiniDB')

        return rc, results, out, err

    def _run_ansible_playbook(self, recipe):
        """Run the proper recipe (playbook)."""
        if (recipe == 'binary_install'):
            playbookname = 'bininstall'
        else:
            playbookname = 'binupgrade'
        p = PlaybookInstall(self, playbookname)
        rc, results, out, err = p.run_cmd()
        self._ansible_file       = p.get_playbook_filename()
        self._extra_vars         = p.get_extra_vars()
        self._inventory_filename = p.get_inventory_filename()

        return rc, results, out, err

    def get_pkgfile(self):
        """Returns pkg file name"""
        return self._pkgfile

    def get_rundir(self):
        """Returns runtime directory"""
        return self._rundir

    #TBD: Don't need for EM yet, since not supporting upgrades yet
    def get_upgfile(self):
        """Returns upgrade pkg file name"""
        return ""

    def get_pkgdir(self):
        """Returns cache package directory"""
        return common.props['cluster.emversionmgr.packages_base']

    def get_sshkey_text(self):
        """Returns sshkey text (to be stored in ansible.cfg)"""
        f = open( common.props['emtools.test.sshkeyfile'] )
        keytext = ''.join(f.readlines())
        return keytext

    def get_postconfig_opts(self):
        """Returns cmd line options to be passed to postConfigure"""
        opts = '-p ssh'
        if self.config()['pm_query']:
            return opts + " -lq"
        else:
            return opts

    def get_playbook_filename(self):
        """
        Return main ansible playbook file
        """
        return self._ansible_file

    def get_extra_vars(self):
        """
        Return extra variable list passed to ansible
        """
        return self._extra_vars

    def get_inventory_filename(self):
        """
        Return inventory file name that was created
        """
        return self._inventory_filename
