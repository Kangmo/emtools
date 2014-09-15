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
import emtools.msg.factreply as factreply

class FactReplyTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        jsonmsg = '''
{ "cluster_info" : {
    "valid" : true,
    "name" : "cluster_1",
    "os_family" : "CentOS",
    "gluster_version" : "",
    "hadoop_version" : "",
    "infinidb_version" : "",
    "em_version" : ""
  },
  "instance_info" : {
    "foo.calpont.com" : {
        "valid" : true,
        "ip_address" : "1.2.3.4",
        "gluster_version" : "",
        "hadoop_version" : ""
    },
    "bar.calpont.com" : {
        "valid" : true,
        "ip_address" : "1.2.3.5",
        "gluster_version" : "",
        "hadoop_version" : ""
    }
  },
  "role_info" : {
    "pm1" : "foo.calpont.com",
    "pm2" : "bar.calpont.com"
  }
}
'''
        f2 = factreply.FactReply(jsonmsg)
        self.assertEqual(f2['cluster_info']['valid'], True)
        self.assertEqual(f2['cluster_info']['name'], 'cluster_1')
        self.assertEqual(f2['cluster_info']['gluster_version'], '')
        self.assertEqual(f2['instance_info']['foo.calpont.com']['valid'], True)
        self.assertEqual(f2['instance_info']['bar.calpont.com']['ip_address'], '1.2.3.5')
        self.assertEqual(f2['role_info']['pm1'], 'foo.calpont.com')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
