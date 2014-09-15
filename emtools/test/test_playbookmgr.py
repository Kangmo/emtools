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
Created on Feb 2, 2014

@author: bwilkinson
'''
import unittest
from emtools.playbookmgr import PlaybookMgr
import testutils
import os
import shutil
from emtools.common.properties import Properties

props = Properties()

class TestPlaybookMgr(unittest.TestCase):


    def setUp(self):
        self.__origclusters = props['emtools.playbookmgr.cluster_base']
        props['emtools.playbookmgr.cluster_base'] = os.path.dirname(__file__)

    def tearDown(self):
        props['emtools.playbookmgr.cluster_base'] = self.__origclusters

    def testRun(self):
        p = PlaybookMgr( 'testbook' )
        p.write_inventory( 'testinv', { 'all' : ['localhost'] } )
        f = open( props['emtools.test.sshkeyfile'] )
        keytext = ''.join(f.readlines())
        p.config_ssh( props['emtools.test.user'], keytext )
         
        rc = p.run_module('testinv', 'all', 'setup', sudo=False)
        
        self.assertTrue( rc['contacted'].has_key( 'localhost' ))
        
        rc, results, out, err = p.run_playbook('smokecheck.yml', 'testinv')
        self.assertEquals(rc, 0)
         
        shutil.rmtree( p.get_rootdir() )

    def testSuccess(self):
        p = PlaybookMgr( 'testbook' )
        p.write_inventory( 'testinv', { 'all' : ['foo.calpont.com', 'bar.calpont.com'] } )
        
        inv = p.read_inventory( 'testinv' )
        self.assertEquals(inv['all'][0], 'foo.calpont.com')
        self.assertEquals(inv['all'][1], 'bar.calpont.com')
        
        ref_file = '%s/test_testinv' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, '%s/testinv' % p.get_rootdir()))
        
        p.config_ssh( 'root', 'some_key_data1234567890' )

        ref_file = '%s/test_ansible.cfg' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, '%s/ansible.cfg' % p.get_rootdir()))

        ref_file = '%s/test_private_key' % os.path.dirname(__file__)
        self.assertTrue( testutils.file_compare(ref_file, '%s/.ssh/private_key' % p.get_rootdir()))
        
        
        shutil.rmtree( p.get_rootdir() )
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
