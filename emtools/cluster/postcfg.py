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
emtools.cluster.postcfg

Class PostConfigureHelper that writes an input script for postConfigure
to support postConfigure automation
'''
from emtools.cluster.configspec import ConfigSpec

class PostConfigureHelper(object):
    '''
    PostConfigureHelper is able to translate from a cluster definition 
    to an input text file that can be piped in on stdin to postConfigure.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def write_input(self, fname, cluster, ptype):
        '''Writes the postConfigure input file.
        
        @param fname - output file location
        @param cluster - the Cluster instance we want to postConfigure
        '''
        self._cluster = cluster
        self._ptype = ptype
        if self._cluster.config()['idbuser'] != 'root':
            self._nonroot = True
        else:
            self._nonroot = False

        # there are a number of differences for 2.2.  cache a boolean to tell us 
        # whether or not we are in that case
        self._using22 = not ConfigSpec._version_greaterthan(self._cluster.config()['idbversion'],'3.0.0-0')
        
        wf = open( fname, 'w' )
        if len(self._cluster.machines()) > 1:
            self._write_multi(wf)
        else:
            self._write_single(wf)
        wf.close()
        
    def _write_multi(self, wf):
        '''Writes input for multi-node configurations.'''        
        wf.write('2\n')   # 2 = multi
        
        # EC2 prompt is version 3.0 and later
        if not self._using22:
            wf.write('n\n')   # not EC2
            
        combined = 2
        if self._cluster.config()['rolespec'].has_key('um'):
            combined = 1
        wf.write('%d\n' % combined) # 2 = combined, 1 = separate
#        if combined == 1 and ConfigSpec._version_greaterthan(self._cluster.config()['idbversion'],'4.5.0-0'):
#            if self._cluster.config()['pm_query']:
#                wf.write('y\n')
#            else:
#                wf.write('n\n')  # pm with user = n; applies to version 4.5 and up

        wf.write('%s\n' % self._cluster.config()['name'])
        wf.write('pm1\n') # local module name always pm1 by convention
        if self._cluster.config()['datdup'] and ConfigSpec._version_greaterthan('4.0.0-0',self._cluster.config()['idbversion']):
            wf.write('y\n')   # y = use datdup
        else:
            self._write_storage_type(wf)
                    
        if self._using22:
            # this is 2.2 - there is a # dbroots prompt here we need to sum up across all nodes
            dbrootcnt = 0
            for m in self._cluster.machines():
                dbrootcnt += len(self._cluster.machines()[m]['dbroots'])
            wf.write('%d\n' % dbrootcnt)            
                        
        if combined == 1:
            self._write_nodes(wf, 'um')
        self._write_nodes(wf, 'pm', nodbroot=self._using22)
        if not self._nonroot:        
            wf.write('y\n')   # y = disable SNMP trap
        else:
            wf.write('n\n')   # n = keep SNMP trap disabled (non-root always defaults off)
        wf.write('n\n')   # n = no external devices
        # note that as it stands right now we cannot run the install in this method 
        # because postConfigure does a getpass() which does not read from STDIN
        # if we want to do this, postConfigure needs an enhancement to bypass that option
        wf.write('y\n')   # perform system install
        wf.write('%s\n' % self._ptype)    # package type
        if self._cluster.config()['datdup']:
            self._write_datdup(wf)
        wf.write('y\n')   # startup system
                
    def _write_nodes(self, wf, role, nodbroot=False):
        count = self._cluster.config()['rolespec'][role]['count']
        wf.write('%d\n' % count)
        wf.write('1\n')   # 1 = starting node num, always 1 by convention
        for i in range(1, count+1):
            name = '%s%d' % (role, i)
            self._write_node(wf,name)
            if role == 'pm' and not nodbroot:
                wf.write('%s\n' % ','.join(str(x) for x in self._cluster.machines()[name]['dbroots']))

    def _write_node(self, wf, node):
        wf.write('%s\n' % self._cluster.machines()[node]['ip'])
        wf.write('\n') # accept ip address same as hostname        
        wf.write('\n') # no NIC #2
        
    def _write_single(self, wf):
        '''Writes input for single-node configurations.'''
        wf.write('1\n')   # 1 = single
        wf.write('%s\n' % self._cluster.config()['name'])
        self._write_storage_type(wf)
        wf.write('%s\n' % ','.join(str(x) for x in self._cluster.machines()['pm1']['dbroots']))
        if not self._nonroot:        
            wf.write('y\n')   # y = disable SNMP trap
        else:
            wf.write('n\n')   # n = keep SNMP trap disabled (non-root always defaults off)

    def _write_datdup(self, wf):
        '''Writes input for the glusterconf portion of postConfigure.'''
        # TODO-make this configurable at some point in the future
        wf.write('2\n')          # number of data copies
        wf.write('existing\n')   # network - existing or dedicated
        wf.write('directory\n')  # storage type - directory or storage (i.e. device)
        
    def _write_storage_type(self, wf):
        if not self._using22:
            # versions 3.0 or later 1 = internal, 2 = external
            # starting at version 4.0 or later, 3 = glusterfs, 4 = hdfs
            if self._cluster.config()['hadoop']:
                wf.write('4\n')   # 4 = hdfs storage
                # TODO - may have to support plugin configuration - not sure if we can
                # trust postConfigure to present the right one as default.  Regardless,
                # not relevant until we add alternate hadoop version support              
                wf.write('\n')   # accept default plugin                  
            elif self._cluster.config()['datdup'] and ConfigSpec._version_greaterthan(self._cluster.config()['idbversion'],'4.0.0-0'):                
                wf.write('3\n')   # 3 = glusterfs storage
            elif self._cluster.config()['storage'] == 'external':
                wf.write('2\n')   # 2 = external storage
            else:
                wf.write('1\n')   # 1 = internal storage
        else:
            # versions earlier than 3.0, 1 = external, 2 = internal
            if self._cluster.config()['storage'] == 'external':
                wf.write('1\n')   # 1 = external storage
            else:
                wf.write('2\n')   # 2 = internal storage
