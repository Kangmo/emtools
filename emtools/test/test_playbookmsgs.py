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
import emtools.msg.playbookreq as playbookreq
import emtools.msg.playbookreply as playbookreply

class PlaybookReqTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testRequestSuccess(self):
        jsonmsg = '''
{ "cluster_name" : "test",
  "playbook_info" : {
    "name" : "a_playbook",
    "hostspec" : "all",
    "extravars" : "var=value"
  }
}
'''
        f2 = playbookreq.PlaybookRequest(jsonmsg)
        self.assertEqual(f2['cluster_name'], 'test')
        self.assertEqual(f2['playbook_info']['name'], 'a_playbook')
        self.assertEqual(f2['playbook_info']['hostspec'], 'all')
        self.assertEqual(f2['playbook_info']['extravars'], 'var=value')

        jsonmsg = '''
{ "cluster_name" : "test",
  "playbook_info" : {
    "name" : "a_playbook",
    "hostspec" : "all",
    "extravars" : ""
  }
}
'''
        f2 = playbookreq.PlaybookRequest(jsonmsg)
        self.assertEqual(f2['playbook_info']['extravars'], '')

    def testRequestNegative(self):
        with self.assertRaisesRegexp(Exception, "Required field.*playbook_info"):
            f2 = playbookreq.PlaybookRequest('{ "cluster_name" : "foo" }')
        with self.assertRaisesRegexp(Exception, "Value.*for field.*playbook_info"):
            f2 = playbookreq.PlaybookRequest('{ "cluster_name" : "foo", "playbook_info" : "foo" }')
        with self.assertRaisesRegexp(Exception, "Required field.*extravars"):
            f2 = playbookreq.PlaybookRequest('{ "cluster_name" : "foo", "playbook_info" : { "playbook_name" : "aname" } }')

    def testReplySuccess(self):
        jsonmsg = '''
{ "cluster_name" : "test",
  "playbook_info" : {
    "name" : "a_playbook",
    "hostspec" : "all",
    "extravars" : "var=value"
  },
  "rc" : 0,
  "stdout" : "some stdout",
  "stderr" : "some stderr"
}
'''
        f2 = playbookreply.PlaybookReply(jsonmsg)
        self.assertEqual(f2['cluster_name'], 'test')
        self.assertEqual(f2['playbook_info']['name'], 'a_playbook')
        self.assertEqual(f2['playbook_info']['hostspec'], 'all')
        self.assertEqual(f2['playbook_info']['extravars'], 'var=value')
        self.assertEqual(f2['rc'], 0)
        self.assertEqual(f2['stdout'], 'some stdout')
        self.assertEqual(f2['stderr'], 'some stderr')

        jsonmsg = '''
{ "cluster_name" : "test",
  "playbook_info" : {
    "name" : "a_playbook",
    "hostspec" : "all",
    "extravars" : "var=value"
  },
  "rc" : 0,
  "stdout" : "some stdout",
  "stderr" : "some stderr",
  "recap_info" : {
      "pm1" : {
        "ok" : 0,
        "changed" : 1,
        "unreachable" : 2,
        "failed" : 3
      }
   }
}
'''
        f2 = playbookreply.PlaybookReply(jsonmsg)
        self.assertEqual(f2['recap_info']['pm1']['ok'], 0)
        self.assertEqual(f2['recap_info']['pm1']['unreachable'], 2)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()