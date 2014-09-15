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

"""
On import the Common module checks for the existence of the AUTOOAM_HOME
environment variable and then automatically instantiates a Properties 
instance for convenience of users.
"""
import os

# we are going to require an environment variable before we start
# on anything else
if not os.environ.has_key('INFINIDB_EM_TOOLS_HOME'):
    raise Exception("INFINIDB_EM_TOOLS_HOME not set!")

import properties

props = properties.Properties()
