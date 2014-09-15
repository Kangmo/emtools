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
emtools.cluster.playbookinstall

Generate/executes ansible playbook for installs and upgrades.
'''
import os
import shutil
import distutils.dir_util
from emtools.playbookmgr import PlaybookMgr
import emtools.common.logutils as logutils
import emtools.common.utils as utils
import emtools.common as common
from pkgfilenameparser import PkgFileNameParser
from emtools.cluster.configspec import ConfigSpec

Log = logutils.getLogger(__name__)

class PlaybookInstall(object):
    '''
    PlaybookGen can be used to generate and execute ansible
    playbooks to perform binary/package installs or upgrades.
    '''

    def __init__(self, cluster, optype):
        '''
        Constructor
        '''
        self._cluster = cluster
        self._optype  = optype
        if ((self._optype != 'pkginstall') and
            (self._optype != 'pkgupgrade') and
            (self._optype != 'bininstall') and
            (self._optype != 'binupgrade')):
            raise Exception("Invalid cluster ansible playbook installer type: %s" % self._optype)
        self._pkgfilenameparser = PkgFileNameParser()

        self._ansible_file = ""
        self._extra_vars   = ""
        self._inventory_filename = "infinidb"
 
    def run_cmd(self):
        '''
        Prepare and run the ansible playbook command for
        the operation type specified in the constructor
        '''
        self._rundir  = self._cluster.get_rundir()
        self._pkgdir  = self._cluster.get_pkgdir()
        self._pkgfile = self._cluster.get_pkgfile()
        self._idbuser = self._cluster.config()['idbuser']
        eflag = self._cluster.config()['enterprise']
        if eflag:
            self._entflag = "true"
        else:
            self._entflag = "false"
        self._version = self._pkgfilenameparser.get_pkg_version(self._pkgfile)
        self._hadoop  = self._cluster.config()['hadoop']
        self._hdfsflag = "false"
        if self._hadoop:
            self._hdfsflag = "true"
        self._upgfile    = self._cluster.get_upgfile()
        self._upgversion = None
        if self._upgfile:
            self._upgversion = self._pkgfilenameparser.get_pkg_version(self._upgfile)
        m = self._cluster.machine('pm1')
        self._pm1_ip = m['ip']
        self._postconfig_opts = self._cluster.get_postconfig_opts()

        # Add -em to postconfig flags for version 4.6 and up
        if self._optype == 'pkginstall':
            if ConfigSpec._version_greaterthan(self._version,'4.6.0-0'):
                self._postconfig_opts += " -em"
            (ansible_yml,cmdargs) = self._prepare_playbook_pkginstall()
        elif self._optype == 'pkgupgrade':
            if ConfigSpec._version_greaterthan(self._upgversion,'4.6.0-0'):
                self._postconfig_opts += " -em"
            (ansible_yml,cmdargs) = self._prepare_playbook_pkgupgrade()
        elif self._optype == 'bininstall':
            if ConfigSpec._version_greaterthan(self._version,'4.6.0-0'):
                self._postconfig_opts += " -em"
            (ansible_yml,cmdargs) = self._prepare_playbook_bininstall()
        elif self._optype == 'binupgrade':
            if ConfigSpec._version_greaterthan(self._upgversion,'4.6.0-0'):
                self._postconfig_opts += " -em"
            (ansible_yml,cmdargs) = self._prepare_playbook_binupgrade()
        else:
            raise Exception("Unsupported ansible playbook type to run: %s" % self._optype)

        extra_playdir = self._cluster.get_extra_playbook_dir()
        p = PlaybookMgr( os.path.basename(self._rundir), extra_playdir )

        # create ansible inventory file with list of hosts;
        # should already exist for an EM-triggered install.
        full_inv_file = '%s/%s' % (p.get_rootdir(), self._inventory_filename)
        if not os.path.exists( full_inv_file ):
            machines = self._cluster.machines()
            iplist = []
            infnodelist = []
            for key in machines:
                m = machines[key]
                iplist.append( m['ip'] )

                # if we are using the EM in invm mode we don't want that
                # node to participate in the normal InfiniDB install
                if key != 'em1':
                    #f.write("key: %s.calpont.com; ip: %s\n" % (key,m['ip']))
                    infnodelist.append( m['ip'] )

            ipdict = { 'all' : iplist, 'infinidb_nodes' : infnodelist }
            p.write_inventory( self._inventory_filename, ipdict )

        # create ansible.cfg file;
        # should already exist for an EM-triggered install.
        full_ans_file = '%s/%s' % (p.get_rootdir(), 'ansible.cfg')
        if not os.path.exists( full_ans_file ):
            keytext = self._cluster.get_sshkey_text()
            p.config_ssh( self._idbuser, keytext )

        # execute playbook thru PlaybookMgr
        self._ansible_file = ansible_yml
        self._extra_vars   = cmdargs
        rc, results, out, err = p.run_playbook(
            ansible_yml,
            self._inventory_filename,
            playbook_args=cmdargs)

        return rc, results, out, err

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

    def _prepare_playbook_pkginstall(self):
        """
        Prepare pkg install using ansible playbook.
        """
        playbook = ('%s/pkginstall.yml' % self._rundir)
        cmdargs = ("\"pkgbasever=%s "
            "pkgver=%s "
            "pkgfile=%s "
            "pkgfilebase=%s "
            "enterprise=%s "
            "pm1_host=%s "
            "postconfig_opts='%s' "
            "hdfs=%s "
            "rundir=%s "
            "pkgdir=%s "
            "\"" % (self._version[0], self._version, self._pkgfile,
                os.path.basename(self._pkgfile), self._entflag, self._pm1_ip,
                self._postconfig_opts, self._hdfsflag, self._rundir,
                self._pkgdir))

        if self._hadoop:
            Log.info("Running pkg install playbook with Hadoop; --extra-vars=%s" % cmdargs)
        else:
            Log.info("Running pkg install playbook; --extra-vars=%s" % cmdargs)

        return (playbook,cmdargs)

    def _prepare_playbook_pkgupgrade(self):
        """
        Prepare pkg upgrade using ansible playbook.
        """
        playbook = ("%s/pkgupgrade.yml" % self._rundir)
        cmdargs = ("\"pm1_host=%s "
            "pkgdir=%s "
            "pkgbasever=%s "
            "upgbasever=%s "
            "upgver=%s "
            "upgfile=%s "
            "upgfilebase=%s "
            "enterprise=%s "
            "postconfig_opts='%s' "
            "\"" % (self._pm1_ip, self._pkgdir, self._version[0], self._upgversion[0],
                self._upgversion, self._upgfile, os.path.basename(self._upgfile),
                self._entflag, self._postconfig_opts))

        Log.info("Running pkg upgrade playbook; --extra-vars=%s" % cmdargs)

        return (playbook,cmdargs)

    def _prepare_playbook_bininstall(self):
        """
        Prepare binary install using ansible playbook.
        """
        playbook = ('%s/bininstall.yml' % self._rundir)
        if self._idbuser == 'root':
            suflag = "no"
        else:
            suflag = "yes"

        cmdargs = ("\"idbuser=%s "
            "pm1_host=%s "
            "sudo_flag=%s "
            "pkgbasever=%s "
            "pkgver=%s "
            "pkgfile=%s "
            "pkgfilebase=%s "
            "postconfig_opts='%s' "
            "hdfs=%s "
            "rundir=%s "
            "pkgdir=%s "
            "\"" % (self._idbuser, self._pm1_ip, suflag, self._version[0],
                self._version, self._pkgfile, os.path.basename(self._pkgfile),
                self._postconfig_opts, self._hdfsflag, self._rundir,
                self._pkgdir))

        if self._hadoop:
            Log.info("Running binary install playbook; with Hadoop; --extra-vars=%s" % cmdargs)
        else:
            Log.info("Running binary install playbook; --extra-vars=%s" % cmdargs)

        return (playbook,cmdargs)

    def _prepare_playbook_binupgrade(self):
        """
        Prepare binary upgrade using ansible playbook.
        """
        playbook = ("%s/binupgrade.yml" % self._rundir)
        cmdargs = ("\"idbuser=%s "
            "pm1_host=%s "
            "pkgdir=%s "
            "upgfile=%s "
            "upgfilebase=%s "
            "postconfig_opts='%s' "
            "\"" % (self._idbuser, self._pm1_ip, self._pkgdir,
                self._upgfile, os.path.basename(self._upgfile),
                self._postconfig_opts))

        Log.info("Running binary upgrade playbook; --extra-vars=%s" % cmdargs)

        return (playbook,cmdargs)
