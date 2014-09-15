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
Created on Mar 21, 2014

@author: bwilkinson
'''
import unittest
import emtools.msg.inventoryreq as inventoryreq

class InventoryReqTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        jsonmsg = '''
{ "cluster_name" : "test",
  "role_info" : {
    "pm1" : "foo.calpont.com",
    "pm2" : "bar.calpont.com"
  }
}
'''
        f2 = inventoryreq.InventoryRequest(jsonmsg)
        self.assertEqual(f2['cluster_name'], 'test')
        self.assertEqual(f2['role_info']['pm1'], 'foo.calpont.com')
        self.assertEqual(f2['role_info']['pm2'], 'bar.calpont.com')

    def testNegative(self):
        with self.assertRaisesRegexp(Exception, "Required field.*role_info"):
            f2 = inventoryreq.InventoryRequest('{ "cluster_name" : "foo" }')
        with self.assertRaisesRegexp(Exception, "Value.*for field.*role_info"):
            f2 = inventoryreq.InventoryRequest('{ "cluster_name" : "foo", "role_info" : "foo" }')
        with self.assertRaisesRegexp(Exception, "Value.*for field.*role_info"):
            f2 = inventoryreq.InventoryRequest('{ "cluster_name" : "foo", "role_info" : ["foo"] }')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()