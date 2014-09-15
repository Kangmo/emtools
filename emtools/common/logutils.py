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
emtools.logutils

A modules that initializes logging on behalf of the importing module.
Typical use is as follows.

Import and instantiate a logger at the module level:

import emtools.logutils as logutils
Log = logutils.getLogger(__name__)

Then make logging calls as usual:

Log.info('...')
Log.warn('...')
Log.error('...')
'''
import os
import logging
import logging.config
import emtools.common as common

# we will first see if a logging.conf file exists and then fall back to
# logging.conf-default
sitelogconf = '%s/conf/logging.conf' % os.environ['INFINIDB_EM_TOOLS_HOME']
deflogconf = '%s/conf/logging.conf-default' % os.environ['INFINIDB_EM_TOOLS_HOME']

logconf = sitelogconf if os.path.exists( sitelogconf ) else deflogconf

logname = common.props['emtools.logname']
logging.config.fileConfig(logconf, defaults={'logname': logname})

def getLogger(name):
    return logging.getLogger(name)
