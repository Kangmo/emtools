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
Created on March 25, 2014

@author: chao
'''
import unittest
import emtools.msg.configreply as configreply

class ConfigReplyTest(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        jsonmsg = '''
{ "cluster_name" : "cluster1", "config" :[{ "em_category" : "UM", "em_parameter" : "TotalUmMemory","value" : "2G" }, { "em_category" : "PM", "em_parameter" : "PmMaxMemorySmallSide", "value" : "64M" }]
}
'''
        f2 = configreply.ConfigReply(jsonmsg)
        self.assertEqual(f2['config'][0]['em_category'], "UM")
        self.assertEqual(f2['config'][0]['value'], "2G")
        
    def testPrint(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
        
