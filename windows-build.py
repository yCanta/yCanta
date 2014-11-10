#!/usr/env python

import os
import sys
import shutil
import tempfile

if os.name != 'nt':
  print 'Windows only!'
  sys.exit(1)

if not len(sys.argv) == 3:
  print 'USAGE: %s PortablePythonDir output-dir' % sys.argv[0]
  print '  Example: D:\yCanta>..\PortablePython\Python-Portable.exe windows-build.py d:\PortablePython d:\output'
  sys.exit(1)

ppydir = sys.argv[1]
workdir = os.path.abspath(sys.argv[2])
requirements = os.path.abspath('requirements.txt')

if not os.path.exists(workdir):
  os.mkdir(workdir)

exclude = [
    'song.db',
    'songs',
    'songbooks',
    'songbook_backup',
    'webapp\\static\\songs',
    'webapp\\static\\songbooks',
    '.git*',
    '.hg*']
print 'EXCLUDE:', exclude

print 'Copying to working dir:', workdir
shutil.copytree('.', os.path.join(workdir, 'yCanta'), ignore=shutil.ignore_patterns(*exclude))
shutil.copytree(ppydir, os.path.join(workdir, 'PortablePython'))

print 'Creating launcher script'
launcher = open(os.path.join(workdir, 'yCanta.bat'), 'w')
launcher.write(r'''cd yCanta
..\PortablePython\Python-Portable.exe start-webapp.py --start-browser
'''.rstrip())
launcher.close()

print 'Installing packages into portable python environment'
easy_install = os.path.join(workdir, 'PortablePython', 'App', 'Scripts', 'easy_install.exe')
print 'EASY_INSTALL:', easy_install
for line in open(requirements):
  if '#' in line:
    continue
  os.system(easy_install + ' ' + line.strip())
os.system(easy_install + ' pip')
# run install via pip too cause of weird portable python bug ... if I do it both ways (easy_install and pip) it works, else it doesn't.
os.system(os.path.join(workdir, 'PortablePython', 'Python-Portable.exe') + ' -m pip install -r ' + requirements)

print 'Creating zip archive: yCanta.zip'
shutil.make_archive('yCanta', 'zip', workdir)

print 'DONE'

#print 'Cleaning up working dir ...'
#shutil.rmtree(workdir)

#exclude = [ os.path.abspath(line) for line in open('.gitignore') if '#' not in line ]
#print 'EXCLUDE:', exclude
#
#for root, dirs, files in os.walk('.'):
#  for i in reversed(range(len(dirs))): # go through indexes backwords because we're doing deletions
#    path = os.path.abspath(os.path.join(root, dirs[i]))
#    if path in exclude:
#      print 'EXCLUDE:', path
#      del dirs[i]
#    else:
#      print 'INCLUDE:', path
#      os.mkdir(os.path.join(workdir, root, dirs[i]))
#
#  for i in reversed(range(len(files))): # go through indexes backwords because we're doing deletions
#    path = os.path.abspath(os.path.join(root, files[i]))
#    if path in exclude:
#      print 'EXCLUDE:', path
#    else:
#      print 'INCLUDE:', path
#      os.mkdir(os.path.join(workdir, root, files[i]))


