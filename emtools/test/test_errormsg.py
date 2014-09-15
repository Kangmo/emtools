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

'''
import unittest
import emtools.msg.errormsg as errormsg

class ConfigReqTest(unittest.TestCase):

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testSuccess(self):
        em = errormsg.ErrorMsg_from_parms("test error")
        self.assertEqual(em['failed'], True)
        self.assertEqual(em['msg'],"test error")
        self.assertFalse(em.has_key('cmd'))
        
        em = errormsg.ErrorMsg_from_parms('test error', cmd='test command')
        self.assertEqual(em['failed'], True)
        self.assertEqual(em['msg'],"test error")
        self.assertEqual(em['cmd'],'test command')

        em = errormsg.ErrorMsg_from_parms('test error', rc=0)
        self.assertEqual(em['failed'], True)
        self.assertEqual(em['msg'],"test error")
        self.assertEqual(em['rc'],0)

        em = errormsg.ErrorMsg_from_parms('test error', stdout='outie', stderr='errie')
        self.assertEqual(em['failed'], True)
        self.assertEqual(em['msg'],"test error")
        self.assertEqual(em['stdout'],'outie')
        self.assertEqual(em['stderr'],'errie')
        
    def testPrint(self):
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
