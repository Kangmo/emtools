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
autooam.common.utils

Miscellaneous utilities
'''

import os,errno
import subprocess
import shlex
import time
import emtools.common as common

def mkdir_p(path):
    '''create all directories on path specified by path argument.  does not 
    complain if directories already exist.'''
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
        
syscall_cb = None

def sleep(sleepfor):
    '''
    framework function to issue a sleep on the host.  Defined here so that
    we have a common place to intercept for unit-test  and not slow it down
    needlessly
    '''
    if not common.props['emtools.unittest']:
        time.sleep(sleepfor)
    
from os import kill
from signal import alarm, signal, SIGALRM, SIGKILL
from subprocess import PIPE, Popen

def syscall_with_timeout(args, timeout = -1):
    '''
    Run a command with a timeout after which it will be forcibly
    killed.
    '''
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    p = Popen(args, stdout = PIPE, stderr = PIPE)
    if timeout != -1:
        signal(SIGALRM, alarm_handler)
        alarm(timeout)
    try:
        stdout, stderr = p.communicate()
        if timeout != -1:
            alarm(0)
    except Alarm:
        pids = [p.pid]
        pids.extend(get_process_children(p.pid))
        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try: 
                kill(pid, SIGKILL)
            except OSError:
                pass
        return -9, '', ''
    return p.returncode, stdout, stderr

def get_process_children(pid):
    p = Popen('ps --no-headers -o pid --ppid %d' % pid, shell = True,
              stdout = PIPE, stderr = PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]
    
def syscall_log(cmd, outfile=None, timeout=-1):
    '''
    syscall_log performs execution of a system call.  It takes two parameters:
    
    @param cmd     - string containing the full command to be executed
    @param outfile - an optional parameter.  If present, it represents a file
                     name that will be opened for append with all stdout/stderr
                     output going to it.  If not present, the full stduout/stderr
                     is returned as a string in the second entry in the return tuple
    @return        - returns a tuple ( <return-code>, <output> ).
    
    Note that if the module object syscall_cb is set then syscall_log is operating
    in debug/unit-test mode.  It will make a call to the syscall_cb with the command
    to be executed.  That function must return a tuple that matches what this 
    function returns - i.e. ( <return code>, <output> )
    '''
    if syscall_cb:
        # this is used for unit testing
        (ret, stdout, stderr) = syscall_cb(cmd)
        if outfile:
            f = open(outfile,'a')
            combinedMsg = ""
            if stdout and len(stdout) > 0:
                combinedMsg += stdout
                if stderr and len(stderr) > 0:
                    combinedMsg += "; "
            if stderr and len(stderr) > 0:
                combinedMsg += "ERROR: "
                combinedMsg += stderr
            f.write(combinedMsg)
            f.close()
            return (ret, "", "")
        else:            
            return (ret, stdout.strip(), stderr.strip())
    else:
        # use shlex to split the command-line args because we have to respect 
        # quoted arguments, etc.
        args = shlex.split(cmd.encode('utf-8'))
        (ret, stdout, stderr) = syscall_with_timeout(args, timeout) 
        if outfile:
            f = open(outfile,'a')
            combinedMsg = ""
            if stdout and len(stdout) > 0:
                combinedMsg += stdout
                if stderr and len(stderr) > 0:
                    combinedMsg += "; "
            if stderr and len(stderr) > 0:
                combinedMsg += "ERROR: "
                combinedMsg += stderr
            f.write(combinedMsg)
            f.close()
            return ( ret, "", "")
        else:
            return ( ret, stdout.strip(), stderr.strip())
