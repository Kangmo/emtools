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
Created on Feb 17, 2014

@author: bwilkinson
'''
import unittest
import emtools.cluster.console as console

class ConsoleTest(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_getsystemstatus(self):
        
        stdout = '''
getsystemstatus   Mon Feb 17 01:20:16 2014

System calpont-1

System and Module statuses

Component     Status                       Last Status Change
------------  --------------------------   ------------------------
System        ACTIVE                       Mon Feb  3 22:36:19 2014

Module um1    ACTIVE                       Mon Feb  3 22:36:14 2014
Module pm1    ACTIVE                       Mon Feb  3 22:35:52 2014
Module pm2    ACTIVE                       Mon Feb  3 22:35:56 2014
Module pm3    ACTIVE                       Mon Feb  3 22:35:57 2014
Module pm4    ACTIVE                       Mon Feb  3 22:35:58 2014

Active Parent OAM Performance Module is 'pm1'
'''
        reslt = console.getsystemstatus(stdout)
        self.assertEqual(reslt['activepm'], 'pm1')
        self.assertEqual(reslt['timestamp'], 'Mon Feb 17 01:20:16 2014')
        self.assertEqual(len(reslt['modules']), 6)
        self.assertEqual(reslt['modules']['System']['status'],'ACTIVE')
        self.assertEqual(reslt['modules']['System']['changed'],'Mon Feb  3 22:36:19 2014')
        self.assertEqual(reslt['modules']['pm4']['status'],'ACTIVE')
        self.assertEqual(reslt['modules']['pm4']['changed'],'Mon Feb  3 22:35:58 2014')

        stdout = '''
getsystemstatus   Sun Apr 13 17:19:46 2014



System single



System and Module statuses



Component     Status                       Last Status Change

------------  --------------------------   ------------------------



**** printSystemStatus Failed =  API Failure return in getSystemStatus API

'''
        reslt = console.getsystemstatus(stdout)
        self.assertEqual(reslt['timestamp'], 'Sun Apr 13 17:19:46 2014')
        self.assertEqual(len(reslt['modules']), 0)


    def test_getprocessstatus(self):
        
        stdout = '''
getprocessstatus   Mon Feb 17 01:18:20 2014

Calpont Process statuses

Process             Module    Status            Last Status Change        Process ID
------------------  ------    ---------------   ------------------------  ----------
ProcessMonitor      um1       ACTIVE            Wed Jan 22 14:38:23 2014       11036
ServerMonitor       um1       ACTIVE            Mon Feb  3 22:35:43 2014       26767
DBRMWorkerNode      um1       ACTIVE            Mon Feb  3 22:35:52 2014       26866
ExeMgr              um1       ACTIVE            Mon Feb  3 22:36:06 2014       27512
DDLProc             um1       ACTIVE            Mon Feb  3 22:36:12 2014       27571
DMLProc             um1       ACTIVE            Mon Feb  3 22:36:19 2014       27616
mysqld              um1       ACTIVE            Mon Feb  3 22:36:01 2014       26697

ProcessMonitor      pm1       ACTIVE            Wed Jan 22 14:38:23 2014       19856
ProcessManager      pm1       ACTIVE            Wed Jan 22 14:38:29 2014       19929
DBRMControllerNode  pm1       ACTIVE            Mon Feb  3 22:35:44 2014       27794
ServerMonitor       pm1       ACTIVE            Mon Feb  3 22:35:45 2014       27811
DBRMWorkerNode      pm1       ACTIVE            Mon Feb  3 22:35:46 2014       27855
DecomSvr            pm1       ACTIVE            Mon Feb  3 22:35:49 2014       27968
PrimProc            pm1       ACTIVE            Mon Feb  3 22:35:53 2014       28000
WriteEngineServer   pm1       ACTIVE            Mon Feb  3 22:35:55 2014       28025

ProcessMonitor      pm2       ACTIVE            Wed Jan 22 14:38:36 2014       19154
ProcessManager      pm2       HOT_STANDBY       Mon Feb  3 22:35:29 2014       15278
DBRMControllerNode  pm2       COLD_STANDBY      Mon Feb  3 22:35:38 2014
ServerMonitor       pm2       ACTIVE            Mon Feb  3 22:35:42 2014       15428
DBRMWorkerNode      pm2       ACTIVE            Mon Feb  3 22:35:51 2014       15514
DecomSvr            pm2       ACTIVE            Mon Feb  3 22:35:54 2014       15546
PrimProc            pm2       ACTIVE            Mon Feb  3 22:35:58 2014       15581
WriteEngineServer   pm2       ACTIVE            Mon Feb  3 22:35:59 2014       15605

'''
        reslt = console.getprocessstatus(stdout)
        self.assertEqual(reslt['timestamp'], 'Mon Feb 17 01:18:20 2014')
        self.assertEqual(len(reslt['modules']), 3)
        self.assertEqual(len(reslt['modules']['pm1']), 8)
        self.assertEqual(reslt['modules']['um1']['ProcessMonitor']['status'],'ACTIVE')
        self.assertEqual(reslt['modules']['um1']['ProcessMonitor']['changed'],'Wed Jan 22 14:38:23 2014')
        self.assertEqual(reslt['modules']['um1']['ProcessMonitor']['pid'],'11036')
        self.assertEqual(len(reslt['modules']['pm2']), 8)
        self.assertEqual(reslt['modules']['pm2']['WriteEngineServer']['status'],'ACTIVE')
        self.assertEqual(reslt['modules']['pm2']['WriteEngineServer']['changed'],'Mon Feb  3 22:35:59 2014')
        self.assertEqual(reslt['modules']['pm2']['WriteEngineServer']['pid'],'15605')
        self.assertEqual(reslt['modules']['pm2']['DBRMControllerNode']['status'],'COLD_STANDBY')
        self.assertEqual(reslt['modules']['pm2']['DBRMControllerNode']['changed'],'Mon Feb  3 22:35:38 2014')
        self.assertEqual(reslt['modules']['pm2']['DBRMControllerNode']['pid'],'')

        stdout = '''
getprocessstatus   Thu Apr 24 20:42:44 2014

Calpont Process statuses

Process             Module    Status            Last Status Change        Process ID
------------------  ------    ---------------   ------------------------  ----------

**** printProcessStatus Failed =  API Failure return in getProcessStatus API
'''
        reslt = console.getprocessstatus(stdout)
        self.assertEqual(reslt['timestamp'], 'Thu Apr 24 20:42:44 2014')
        self.assertEqual(len(reslt['modules']), 0)

        
    def test_getactivealarms(self):
        
        stdout = '''
getactivealarms   Sun Mar 23 20:47:45 2014

Active Alarm List:
        
AlarmID           = 6
Brief Description = DISK_USAGE_LOW
Alarm Severity    = MINOR
Time Issued       = Sun Mar 23 06:23:45 2014
Reporting Module  = pm1
Reporting Process = ServerMonitor
Reported Device   = /

AlarmID           = 6
Brief Description = DISK_USAGE_LOW
Alarm Severity    = MINOR
Time Issued       = Sun Mar 23 06:25:21 2014
Reporting Module  = pm6
Reporting Process = ServerMonitor
Reported Device   = /

AlarmID           = 5
Brief Description = DISK_USAGE_MED
Alarm Severity    = MAJOR
Time Issued       = Sun Mar 23 07:37:07 2014
Reporting Module  = pm1
Reporting Process = ServerMonitor
Reported Device   = /
'''
          
        reslt = console.getactivealarms(stdout)
        self.assertEqual(reslt['timestamp'], 'Sun Mar 23 20:47:45 2014')
        self.assertEqual(len(reslt['alarms']), 3)
        self.assertEqual(reslt['alarms'][0]['AlarmId'], '6')
        self.assertEqual(reslt['alarms'][0]['Brief Description'], 'DISK_USAGE_LOW')
        self.assertEqual(reslt['alarms'][1]['Alarm Severity'], 'MINOR')
        self.assertEqual(reslt['alarms'][1]['Time Issued'], 'Sun Mar 23 06:25:21 2014')
        self.assertEqual(reslt['alarms'][1]['Reporting Module'], 'pm6')
        self.assertEqual(reslt['alarms'][2]['Reporting Process'], 'ServerMonitor')
        self.assertEqual(reslt['alarms'][2]['Reported Device'], '/')
        
    def test_gettablelocks(self):
        
        stdout = '''
 There is 1 table lock

  Table     LockID  Process  PID    Session  Txn     CreationTime              State    DBRoots      
  test.foo  15949   DMLProc  17916  14029    340729  Sun Mar 23 20:45:41 2014  LOADING  1,2,3,4,5,6  
'''
        reslt = console.gettablelocks(stdout)
        self.assertEqual(len(reslt['locks']), 1)
        self.assertEqual(reslt['locks'][0]['Table'], 'test.foo')
        self.assertEqual(reslt['locks'][0]['LockID'], '15949')
        self.assertEqual(reslt['locks'][0]['Process'], 'DMLProc')
        self.assertEqual(reslt['locks'][0]['PID'], '17916')
        self.assertEqual(reslt['locks'][0]['Session'], '14029')
        self.assertEqual(reslt['locks'][0]['Txn'], '340729')
        self.assertEqual(reslt['locks'][0]['CreationTime'], 'Sun Mar 23 20:45:41 2014')
        self.assertEqual(reslt['locks'][0]['State'], 'LOADING')
        self.assertEqual(reslt['locks'][0]['DBRoots'], '1,2,3,4,5,6')
        
        stdout = '''
 There is 1 table lock

  Table            LockID  Process  PID    Session  Txn     CreationTime              State    DBRoots      
  longertable.foo  15949   DMLProc  17916  14029    340729  Sun Mar 23 20:45:41 2014  LOADING  1,2,3,4,5,6  
'''
        reslt = console.gettablelocks(stdout)
        self.assertEqual(reslt['locks'][0]['Table'], 'longertable.foo')
        self.assertEqual(reslt['locks'][0]['LockID'], '15949')

    def test_gettablelocks_neg(self):
        
        # try out a case where the columns have changed or are screwed up
        stdout = '''
 There is 1 table lock

  Table     LockBad  Process  PID    Session  Txn     CreationTime              State    DBRoots      
  test.foo  15949    DMLProc  17916  14029    340729  Sun Mar 23 20:45:41 2014  LOADING  1,2,3,4,5,6  
'''
        reslt = console.gettablelocks(stdout)
        self.assertEqual(reslt['locks'][0]['CreationTime'], 'Sun Mar 23 20:45:41 2014')
        self.assertEqual(reslt['locks'][0]['LockID'], '')

        # first column messed up - this shouldn't parse as a lock
        stdout = '''
 There is 1 table lock

  BadTable   LockID  Process  PID    Session  Txn     CreationTime              State    DBRoots      
  test.foo   15949   DMLProc  17916  14029    340729  Sun Mar 23 20:45:41 2014  LOADING  1,2,3,4,5,6  
'''
        reslt = console.gettablelocks(stdout)
        self.assertEqual(len(reslt['locks']),0)

        # last column messed up
        stdout = '''
 There is 1 table lock

  Table     LockID  Process  PID    Session  Txn     CreationTime              State    FooRoots      
  test.foo  15949   DMLProc  17916  14029    340729  Sun Mar 23 20:45:41 2014  LOADING  1,2,3,4,5,6  
'''
        reslt = console.gettablelocks(stdout)
        self.assertEqual(reslt['locks'][0]['CreationTime'], 'Sun Mar 23 20:45:41 2014')
        # this case is a strange but without the column header to rely on we include additional text
        self.assertEqual(reslt['locks'][0]['State'], 'LOADING  1,2,3,4,5,6')
        self.assertEqual(reslt['locks'][0]['DBRoots'], '')

        # multiple columns messed up
        stdout = '''
 There is 1 table lock

  Table     LockID  Process  XID    Fession  Txn     CreationTime              State    DBRoots      
  test.foo  15949   DMLProc  17916  14029    340729  Sun Mar 23 20:45:41 2014  LOADING  1,2,3,4,5,6  
'''
        reslt = console.gettablelocks(stdout)
        self.assertEqual(reslt['locks'][0]['CreationTime'], 'Sun Mar 23 20:45:41 2014')
        # this case is a strange but without the column header to rely on we include additional text
        self.assertEqual(reslt['locks'][0]['Process'], 'DMLProc  17916  14029')
        self.assertEqual(reslt['locks'][0]['State'], 'LOADING')
        self.assertEqual(reslt['locks'][0]['DBRoots'], '1,2,3,4,5,6')
                
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
