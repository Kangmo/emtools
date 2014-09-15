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
Created on Feb 16, 2014

@author: bwilkinson
'''
import unittest
import emtools.msg.commandreq as commandreq


class ConsoleCmdTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        m1 = commandreq.CommandReq('{ "cluster_name" : "cluster1", "command" : "startsystem" }')
        self.assertEqual(m1['cluster_name'], "cluster1")
        self.assertEqual(m1['command'], "startsystem")

        m1 = commandreq.CommandReq('{ "cluster_name" : "cluster1", "command" : "stopsystem", "args" : "-y" }')
        self.assertEqual(m1['cluster_name'], "cluster1")
        self.assertEqual(m1['command'], "stopsystem")
        self.assertEqual(m1['args'], "-y")



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
