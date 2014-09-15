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
Created on Feb 6, 2014

@author: bwilkinson
'''
import unittest
import emtools.common.properties as properties
import os

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testDefaults(self):
        props = properties.Properties( unittest = True )
        self.assertEqual(props['emtools.playbookmgr.cluster_base'], '%s/clusters' % (os.environ['INFINIDB_EM_TOOLS_HOME']))

        # we are going to force a test site.properties to load
        cpath = os.environ['INFINIDB_EM_TOOLS_HOME']
        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf' % os.path.dirname(__file__)

        props = properties.Properties()
        self.assertEqual(props['emtools.playbookmgr.cluster_base'], '%s/clusters' % (os.environ['INFINIDB_EM_TOOLS_HOME']))
        self.assertEqual(props['cluster.cluster.emrole'], 'pm1')

        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf2' % os.path.dirname(__file__)

        props = properties.Properties()
        self.assertEqual(props['emtools.playbookmgr.cluster_base'], 'different_path')

        os.environ['INFINIDB_EM_TOOLS_HOME'] = cpath
        
    def testNegative(self):
        cpath = os.environ['INFINIDB_EM_TOOLS_HOME']
        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf1' % os.path.dirname(__file__)

        with self.assertRaisesRegexp(Exception,"File contains no section headers"):        
            props = properties.Properties()

        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf3' % os.path.dirname(__file__)

        with self.assertRaisesRegexp(Exception,"non-boolean value"):        
            props = properties.Properties()

        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf4' % os.path.dirname(__file__)

        with self.assertRaisesRegexp(Exception,"non-integer value"):        
            props = properties.Properties()

        os.environ['INFINIDB_EM_TOOLS_HOME'] = cpath
        
    def testInclude(self):
        cpath = os.environ['INFINIDB_EM_TOOLS_HOME']
        
        tmpfile = '/tmp/site.properties'
        w = open(tmpfile, 'w')
        w.write('''
[defaults]
cluster.cluster.emrole = pm1
cluster.cluster.emport = 8100
cluster.cluster.eminvm = True
''')
        w.close()
        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf5' % os.path.dirname(__file__)

        props = properties.Properties()
        self.assertEqual(props['cluster.cluster.emrole'], 'pm1')
        self.assertEqual(props['cluster.cluster.emport'], 8100)
        self.assertEqual(props['cluster.cluster.eminvm'], True)

        os.remove(tmpfile)
        
        # try loading again without the file there
        props = properties.Properties()
        self.assertEqual(props['cluster.cluster.emrole'], 'um1')
        
        os.environ['INFINIDB_EM_TOOLS_HOME'] = cpath
        
    def testAddtl(self):
        addtl = {
            'foo.version': (str, 'Latest'),
            'foo.role'   : (str, 'um1'),
        }
        props = properties.Properties( unittest = True, addtl_defns=addtl )
        self.assertEqual(props['foo.version'], 'Latest')
        self.assertEqual(props['foo.role'], 'um1')

        cpath = os.environ['INFINIDB_EM_TOOLS_HOME']
        
        tmpfile = '/tmp/site.properties'
        w = open(tmpfile, 'w')
        w.write('''
[defaults]
foo.version = bar
''')
        w.close()
        os.environ['INFINIDB_EM_TOOLS_HOME'] = '%s/conf' % os.path.dirname(__file__)

        props = properties.Properties( addtl_defns=addtl, addtl_site=tmpfile )
        self.assertEqual(props['foo.version'], 'bar')

        props = properties.Properties( addtl_site='foobarred' )
        self.assertEqual(props['emtools.playbookmgr.cluster_base'], '%s/clusters' % (os.environ['INFINIDB_EM_TOOLS_HOME']))

        # we want no emtools site.properties for these tests
        os.environ['INFINIDB_EM_TOOLS_HOME'] = '/tmp/conf'

        # tests the same thing but without an emtools site.properties file
        props = properties.Properties( addtl_site='foobarred' )
        self.assertEqual(props['emtools.playbookmgr.cluster_base'], '%s/clusters' % (os.environ['INFINIDB_EM_TOOLS_HOME']))

        # now check an addtl site file when there is no emtools site
        props = properties.Properties( addtl_defns=addtl, addtl_site=tmpfile )
        self.assertEqual(props['emtools.playbookmgr.cluster_base'], '%s/clusters' % (os.environ['INFINIDB_EM_TOOLS_HOME']))
        self.assertEqual(props['foo.version'], 'bar')

        os.remove(tmpfile)
        os.environ['INFINIDB_EM_TOOLS_HOME'] = cpath

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
