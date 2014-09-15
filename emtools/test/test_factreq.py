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
Created on Jan 31, 2014

@author: bwilkinson
'''
import unittest
import emtools.msg.factreq as factreq

class FactReqTest(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        f2 = factreq.FactRequest('{ "cluster_name" : "cluster1", "hostnames" : [ "differenthost.calpont.com" ], "ssh_user" : "root", "ssh_key" : "axj123123" }')
        self.assertEqual(f2['hostnames'][0], "differenthost.calpont.com")
        self.assertEqual(f2['ssh_key'], "axj123123")

        f4 = factreq.FactRequest('{ "cluster_name" : "cluster1", "hostnames" : [ "differenthost.calpont.com" ], "ssh_user" : "root", "ssh_pass" : "axj123123", "ssh_port" : 456 }')
        self.assertEqual(f4['hostnames'][0], "differenthost.calpont.com")
        self.assertEqual(f4['ssh_port'], 456)
        
    def testPrint(self):
        f4 = factreq.FactRequest('{ "cluster_name" : "cluster1", "hostnames" : [ "differenthost.calpont.com" ], "ssh_user" : "root", "ssh_key" : "axj123123", "ssh_port" : 456 }')
        targ = '%s' % f4
        ref = '''{
    "cluster_name": "cluster1", 
    "hostnames": [
        "differenthost.calpont.com"
    ], 
    "ssh_key": "axj123123", 
    "ssh_port": 456, 
    "ssh_user": "root"
}'''
        # this helps figure out any difference that is about to be flagged
        for i in range(0, len(ref)):
            if targ[i] != ref[i]:
                print 'difference at position %d: %s != %s' % (i, targ[i], ref[i])
        self.assertEqual('%s'% f4, ref)
        
    def testNegative(self):
        # test empty hostnames
        with self.assertRaisesRegexp(Exception,"Length of value.*hostnames"):        
            f1 = factreq.FactRequest('{ "cluster_name" : "c1", "hostnames" : [], "ssh_user" : "root" }')

        # test missing hostnames
        with self.assertRaisesRegexp(Exception,"Required field.*hostnames"):        
            f1 = factreq.FactRequest('{ "cluster_name" : "c1", "ssh-key" : "123", "ssh_user" : "root" }')

        # test type error in hostnames
        with self.assertRaisesRegexp(Exception,"Failed to validate field.*hostnames"):        
            f1 = factreq.FactRequest('{ "cluster_name" : "c1", "hostnames" : [ 1,2,3], "ssh_user" : "root" }')

        # test missing cluster_name
        with self.assertRaisesRegexp(Exception,"Required field.*cluster_name"):        
            f1 = factreq.FactRequest('{ "hostnames" : ["abc"], "ssh_user" : "root" }')

        # test empty cluster_name
        with self.assertRaisesRegexp(Exception,"cluster_name.*cannot be blank"):        
            f1 = factreq.FactRequest('{ "cluster_name" : "", "hostnames" : ["abc"], "ssh_user" : "root" }')

        # test missing ssh_user
        with self.assertRaisesRegexp(Exception,"Required field.*ssh_user"):        
            f1 = factreq.FactRequest('{ "cluster_name" : "c1", "hostnames" : ["abc"] }')

        # bad JSON
        with self.assertRaisesRegexp(ValueError,"No JSON object could be decoded"):        
            f1 = factreq.FactRequest('this is not really json')

        # try accessing a field that never existed in the message
        with self.assertRaisesRegexp(KeyError,"not_there"):        
            f1 = factreq.FactRequest('{ "cluster_name" : "c1", "hostnames" : ["foo"], "ssh_user" : "root", "ssh_key" : "axj123123" }')
            print f1['not_there']

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
        
