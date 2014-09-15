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
emtools.cluster.console

This module contains functions that exist for the purpose of translating
calpontConsole command output to a JSON structure.  Not all calpontConsole
commands require this translation because many do not have any particular
output.  The proper usage of this module is to check for the existence of
a function that matches the name of a calpontConsole command.  It takes 
stdout output from calpontConsole execution and returns a dictionary that
can easily be transformed into JSON.

Contains:
    getsystemstatus()
'''
import re

def getsystemstatus(stdout):
    '''
    Parse the output from getsystemstatus into JSON
    '''
    reslt = {}
    reslt['modules'] = {}
    header = re.compile('getsystemstatus\s+(.*)')
    seps = re.compile('(\-+)\s+(\-+)\s+(\-+)')
    activepm = re.compile('Active Parent OAM Performance Module is \'(\w+)\'')
    stage = 0
    fields = []
    for l in stdout.split('\n'):
        if stage == 0:
            # looking for the command header and timestamp
            mat = header.match(l)
            if mat:
                reslt['timestamp'] = mat.group(1)
                stage = 1
        elif stage == 1:
            # looking for the column separator line
            mat = seps.match(l)
            if mat:
                fields.append( (mat.start(1), mat.end(1)))
                fields.append( (mat.start(2), mat.end(2)))
                fields.append( (mat.start(3), mat.end(3)))
                stage = 2
        elif stage == 2:
            mat = activepm.match(l)
            if mat:
                reslt['activepm'] = mat.group(1)
            elif len(l) > fields[2][0]:
                component = l[fields[0][0]:fields[0][1]].strip()
                if component.find('Module ') == 0:
                    component = component[7:]
                elif component.find('System') == 0:
                    component = 'System'
                else:
                    continue
                status = l[fields[1][0]:fields[1][1]].strip()
                changed = l[fields[2][0]:fields[2][1]].strip()
                reslt['modules'][component] = { "status" : status, "changed": changed }
    
    return reslt

def getprocessstatus(stdout):
    '''
    Parse the output from getprocessstatus into JSON
    '''
    reslt = {}
    reslt['modules'] = {}
    header = re.compile('getprocessstatus\s+(.*)')
    seps = re.compile('(\-+)\s+(\-+)\s+(\-+)\s+(\-+)\s+(\-+)')
    stage = 0
    fields = []
    for l in stdout.split('\n'):
        if stage == 0:
            # looking for the command header and timestamp
            mat = header.match(l)
            if mat:
                reslt['timestamp'] = mat.group(1)
                stage = 1
        elif stage == 1:
            # looking for the column separator line
            mat = seps.match(l)
            if mat:
                fields.append( (mat.start(1), mat.end(1)))
                fields.append( (mat.start(2), mat.end(2)))
                fields.append( (mat.start(3), mat.end(3)))
                fields.append( (mat.start(4), mat.end(4)))
                fields.append( (mat.start(5), mat.end(5)))
                stage = 2
        elif stage == 2:
            # we intentionally check the 4th field since pid can be blank
            if len(l) > fields[3][0]:
                process = l[fields[0][0]:fields[0][1]].strip()
                module = l[fields[1][0]:fields[1][1]].strip()
                if not module[0:2] in ( 'pm', 'um' ):
                    continue
                status = l[fields[2][0]:fields[2][1]].strip()
                changed = l[fields[3][0]:fields[3][1]].strip()
                if len(l) > fields[4][0]:
                    pid = l[fields[4][0]:fields[4][1]].strip()
                else:
                    pid = ''
                if not reslt['modules'].has_key( module ):
                    reslt['modules'][module] = {}
                reslt['modules'][module][process] = { "status" : status, "changed": changed, "pid" : pid }
    
    return reslt

def getactivealarms(stdout):
    reslt = {}
    reslt['alarms'] = []
    header = re.compile('getactivealarms\s+(.*)')
    stage = 0
    cur_alarm = None
    for l in stdout.split('\n'):
        if stage == 0:
            # looking for the command header and timestamp
            mat = header.match(l)
            if mat:
                reslt['timestamp'] = mat.group(1)
                stage = 1
        elif stage == 1:
            if l.find('AlarmID') == 0:
                if cur_alarm:
                    reslt['alarms'].append( cur_alarm )
                cur_alarm = {}
                cur_alarm['AlarmId'] = l[20:]
            elif l.find('Brief Description') == 0:
                cur_alarm['Brief Description'] = l[20:]
            elif l.find('Alarm Severity') == 0:
                cur_alarm['Alarm Severity'] = l[20:]
            elif l.find('Time Issued') == 0:
                cur_alarm['Time Issued'] = l[20:]
            elif l.find('Reporting Module') == 0:
                cur_alarm['Reporting Module'] = l[20:]
            elif l.find('Reporting Process') == 0:
                cur_alarm['Reporting Process'] = l[20:]
            elif l.find('Reported Device') == 0:
                cur_alarm['Reported Device'] = l[20:]
            
    if cur_alarm:
        reslt['alarms'].append( cur_alarm )
    
    return reslt

def gettablelocks(stdout):
    fields = ['Table','LockID','Process','PID','Session','Txn','CreationTime','State','DBRoots']
    reslt = {}
    reslt['locks'] = []
    fieldindices = []
    stage = 0
    for l in stdout.split('\n'):
        l = l.strip()
        if stage == 0:
            # looking for the row with column headers
            if l.find('Table') == 0:
                cur = 'Table'
                curstart = 0
                for i in range(1,len(fields)):
                    next = l.find(fields[i])
                    if next == -1:
                        # this is an error scenario - there is a column that we 
                        # expect to find and did not.
                        fieldindices.append( (fields[i], -1, -1) )
                    else:
                        fieldindices.append( (cur, curstart, next-2) )
                        cur = fields[i]
                        curstart = next
                fieldindices.append( (cur, curstart, -1 ) )
                stage = 1
        elif stage == 1:
            l = l.strip()
            lock = {}
            if l:
                for f in fieldindices:
                    # f is 3-tuple, name, start, end
                    if f[1] == -1:
                        # this is a special case if we didn't find a column header
                        lock[f[0]] = ''                        
                    elif f[2] == -1:
                        # this is a special case for the last field in the string
                        lock[f[0]] = l[f[1]:].strip()
                    else:
                        lock[f[0]] = l[f[1]:f[2]].strip()
                reslt['locks'].append(lock)
                
    return reslt