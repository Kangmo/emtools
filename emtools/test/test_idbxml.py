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
Created on Feb 4, 2014

@author: bwilkinson
'''
import unittest
from emtools.idbxml import IdbXml
import os

class IdbXmlTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        xml_file = '%s/test_Calpont.xml' % os.path.dirname(__file__)
        
        idbxml = IdbXml( xml_file )

        pms = idbxml.get_pms()
        self.assertEqual(len(pms), 4)
        self.assertEqual(pms[0]['role'], 'pm1')
        self.assertEqual(pms[0]['ip_address'], '10.0.3.56')
        self.assertEqual(pms[0]['hostname'], 'cdh-data1')

        ums = idbxml.get_ums()
        self.assertEqual(len(ums), 1)
        self.assertEqual(ums[0]['role'], 'um1')
        self.assertEqual(ums[0]['ip_address'], '10.0.3.55')
        self.assertEqual(ums[0]['hostname'], 'cdh-head')
        value = idbxml.get_parm('HashJoin', 'MaxBuckets')
        self.assertEqual(value, '128')

        value = idbxml.get_parm('NoSection', 'NoParm')
        self.assertEqual(value, '')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
