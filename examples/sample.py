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
Created on Feb 3, 2014

@author: bwilkinson
'''
from emtools.playbookmgr import PlaybookMgr
import emtools.factreq as factreq
import emtools.factreply as factreply
import emtools.idbxml as idbxml

import os

if __name__ == '__main__':
    
    
    p = PlaybookMgr( 'cdh-head' )

    ssh_key = '''    
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA0NQO/C7ir5tgqrQVX6utjGxrhCqywzWuB80JOivOugVCzDqejHmI/nu8EPu3
F+3LmpI34jXh8+AhyL8Dn7Cdw43++fx8zAGPSalOygfRDENEWptCey6R5xQw4GxoyxSy8DfmG/yj
7IXWNojjrR5xkewKSS7xgDjiNXcFdC0euCsRihTG27d3PZBW9ayEEwMeXThjAZEuT/SW+6WdPWsb
9w9w5vvYWhQtr1kKeaHojnwMqxfnjiTVIs66ck2dwH6mjN0i/PI+zFZW5YF5zuPczr92fiPMnsum
8iAbGUubrqM/SIjkoO4P5vp7hYTXaVM3Kn41Sqj4z8SlDJ4WTBgqDQIDAQABAoIBAFa8zeCXRNa1
zef5VqtfLn2WBu5locyNPlTFKCD+UyZWyxDzBCnKzUkOceYH91u8DIaOVyHhSZG3NbEhDctFW7H/
B7oj0l4WA8MPzMcDiiPyyLBtrqZliHqXm1mMDdbUKSK3xR84x4mVaY1LPG4KqBd5GCifk/WzKtoU
LrK7jvflQ3oqjVTrIifvZYIh4C4NaamotjztIZPtwsTDiIYk0SjxqJQytswIiQt/wPHOR3uHpyQ8
Ak6SNzeWtV3ghftjLJDCCyb32fE2j15Tw4bNimhS2Z34kG5INLSy5plwfPVRBPP2kUJk3KVZtpo9
foG9VxFDiwAve0jmDQKpacdjYS0CgYEA72Bdj+xWrUElSm+OPuhTuo7/Y/lod4RrnBGwPeyng6E2
4v/aZwBc8eIxZNtb43VZm4YO0iJFr+bf4i5I7/ptvp2iskRAskcUpUkCymhFr4DxDcpamJjdV2vr
AdD8bLvd2NVmrOpCWHvbKVrQTyNeKeBJE8mnRFsaCcRZuokaJXsCgYEA31Sb/kclXHq0v3LywKrY
GGF5jyGOoDur06BYumuB2s8BfyE1yOY8Fx01OQ6K2UjOAIRzwP3fJb5pagLdapRQky6GNpeUi9fB
8ms2ygKg6WUxX4Zx9C/U1X4HeYZjOuTVdebJDSr+cpDqaWMQw8EqxbJ1yzOL7/HuZ40CjQ10pBcC
gYA+6Uytrqd5EU4Dqh3wWo7m0P4+ACZ8gsjlU6DGJZRA+/W44xU7TNUgnRnuL9iOhyDtxuXOREOc
X0kn4JI6v85n8nX39Ags0pGSfwXEvHLUFUdFIJF+2W4Ss8In0A0HZrh/bFZ3y3l0V9jZnYxxwBHX
X6LVGIJlbKwDNR9/7th4UQKBgQCqsfWk7WYOAC+kYMxQHIScZexOTNzBdbpIPzdyDPescSn4rD56
thbZp9ZlLMtNdksVtCbxLFlhdN8HSvdHHeNUC2xDz6mXFSrFCdNPpaCto02QcKcqd2CaaQB3jxLL
EdphiirDKMhgcojoUfKfXEY/4r4LuPNNS0Hn3axEeTNcswKBgQCK6Ky4qVt+9DuAZ7Ti3G+X4E0x
PVuo125oFHUtJ1B3JZFO+iWM4hZvw6NKillGNuE0S30FBudXI3GI/0Wb8cl7vdnftISzEA+xrZUo
LMqvuXd1S1KFxtNLLrcvWVYecurE3+jWktJpCw/r1q5BN9grOdEDDYNN44Kh1Ap0QrD4eQ==
-----END RSA PRIVATE KEY-----'''

    p.config_ssh( 'root', ssh_key )
    
    hosts = [
        'cdh-head.calpont.com',
        'cdh-data1.calpont.com',
        'cdh-data2.calpont.com',
        'cdh-data3.calpont.com',
        #'cdh-data4.calpont.com'
        ]
    
    reqdict = {
        'cluster_name':'cdh-head',
        'hostnames':hosts,
        'ssh_user':'root',
        'ssh_key':ssh_key
    }
    
    req = factreq.FactRequest_from_dict( reqdict )
    print '%s' % req

    # todo - handle case where use only specifies one machine of infinidb cluster
    # run site_facts first, then check to make sure any infinidb machine is in the
    # inventory.  Then rerun setup & site_facts, etc.
    p.write_inventory( 'default', { 'all' : hosts })

    cluster_valid = True
    cluster_dist = ''
    cluster_reason = ''
    valid_instances = 0
    cluster_gluster = ''
    cluster_hadoop = ''
    cluster_infinidb = ''
    infinidb_host = ''
    
    instance_info = {}
    reslt = p.run_module( 'default', 'all', 'setup' )
    role_info = {}
    
    for h in reslt['dark']:
        instance_info[h] = dict( valid=False )
    for h in reslt['contacted']:
        host_facts = reslt['contacted'][h]['ansible_facts']
        if not cluster_dist:
            cluster_dist = host_facts['ansible_distribution']
        elif cluster_dist != host_facts['ansible_distribution']:
            cluster_valid = False
            cluster_reason = 'Multiple distributions: %s and %s' % (cluster_dist, host_facts['ansible_distribution']) 
        instance_info[h] = dict( valid=True, ip_address=host_facts['ansible_default_ipv4']['address'] )
        
        site_reslt = p.run_module( 'default', h, 'site_facts' )
        print site_reslt
        site_facts = site_reslt['contacted'][h]['ansible_facts']
        instance_info[h]['gluster_version'] = site_facts['gluster_version']
        if not cluster_gluster and instance_info[h]['gluster_version']:
            cluster_gluster = instance_info[h]['gluster_version']
        instance_info[h]['hadoop_version'] = site_facts['hadoop_version']
        if not cluster_hadoop and instance_info[h]['hadoop_version']:
            cluster_hadoop = instance_info[h]['hadoop_version']
        if not cluster_infinidb and site_facts['infinidb_version']:
            cluster_infinidb = site_facts['infinidb_version']
            infinidb_host = h
        valid_instances = valid_instances + 1
        
    role_info = {}
    if valid_instances == 0:
        cluster_valid = False
        cluster_reason = 'No reachable hosts'
    elif cluster_infinidb:
        # we found infinidb software.  Run our getinfo playbook to retrieve Calpont.xml
        rc = p.run_playbook('getinfo.yml', 'default')
        if rc == 0:
            # this playbook will write Calpont.xml files to /tmp/<host>-Calpont.xml
            shortname = infinidb_host[0:infinidb_host.find('.')]
            xml = idbxml.IdbXml( '/tmp/%s-Calpont.xml' % shortname )
            
            for r in xml.get_all_roles():
                # eoch role here has role= and ip_address= but we need to put
                # map role to hostname for our reply.
                role = r['role']
                ip = r['ip_address']
                host = ''
                for i in instance_info.iterkeys():
                    if instance_info[i]['ip_address'] == ip:
                        host = i
                if not host:
                    host = ip
                role_info[role] = host
        
    cluster_info = dict(
        valid=cluster_valid,
        name='',
        os_family=cluster_dist,
        reason=cluster_reason,
        gluster_version=cluster_gluster,
        hadoop_version=cluster_hadoop,
        infinidb_version=cluster_infinidb,
        em_version=''
        )
        
    reply = factreply.FactReply_from_dict( { "cluster_info" : cluster_info, "instance_info" : instance_info, "role_info": role_info})
    print '%s' % reply
    #p.run_playbook( 'getinfo.yml', 'default' )
