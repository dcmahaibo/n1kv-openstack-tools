'''
Author: Aaron Zhang (fenzhang)

Monitoring script
'''

import argparse
import ConfigParser
import os
import packaging_v2
import shutil

from packaging_v2 import _chdir, _mkdir, _listdir, _rename

MAXIUM = 10
components = ['neutron', 'python-neutronclient']
rdos = {'neutron': \
        os.path.join(os.getcwd(), 'openstack-neutron-2014.1-19.el6ost.src.rpm'),
        'python-neutronclient': \
        os.path.join(os.getcwd(),'python-neutronclient-2.3.4-1.el6ost.src.rpm')}


# packaging
pwd = os.getcwd()
parser = argparse.ArgumentParser()
parser.add_argument('--conf', help = 'location of packaging.conf file',
                    required = True)
parser.add_argument(
    '--force',
    help = 'force to recreate package no matter if cisco code is changed',
    action = 'store_true')
args = parser.parse_args()
update = 0
for comp in components:
    agent = packaging_v2.Packaging(os.path.join(pwd, args.conf), comp)
    update |= agent.repackage(rdos[comp], args.force)

if not update:
    print '!!!ALREADY UP-TO-DATE, SKIP BUILDING AND EXIT!!!'
    exit(0)


# backing up
configParser = ConfigParser.RawConfigParser()
configParser.read(os.path.join(pwd, args.conf))
dump_dir = configParser.get('general', 'dump_dir')
TOPDIR = configParser.get('general', 'TOPDIR')    

if not os.path.exists(dump_dir):
    _mkdir(dump_dir)

_chdir(dump_dir)
folders = _listdir('.')
if not folders:
    _mkdir('0')
    _mkdir('LATEST')
else:
    builds = sorted([int(folder) for folder in folders if folder.isdigit()])
    num = len(builds)
    oldest, newest = builds[0], builds[-1]
    if num == MAXIUM:
        print '# rm -rf ', oldest
        shutil.rmtree(str(oldest))
    _rename('LATEST', str(newest + 1))
    _mkdir('LATEST')

for comp in components:
    _chdir(os.path.join(TOPDIR, comp, 'RPMS', 'noarch'))
    for afile in _listdir('.'):
        shutil.copy(afile, os.path.join(dump_dir, 'LATEST'))
