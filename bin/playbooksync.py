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

#!/usr/bin/env python
'''
playbooksync.py

synchronize a playbook from the current template
'''
import getopt
import os, sys

from emtools.playbookmgr import PlaybookMgr
    
#-------------------------------------------------------------------------------
# main entry point
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "usage: playbooksync.py <cluster-name>"
        sys.exit(1)
        
    cluster = sys.argv[1]
    
    pmgr = PlaybookMgr( cluster )
    print 'Playbook for %s is synced' % cluster
    
    sys.exit(0)
