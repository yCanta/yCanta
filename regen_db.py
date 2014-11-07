#!/usr/bin/env python
from webapp.model import Song, Songbook, hub
try: # try c version for speed then fall back to python
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET
import xml.parsers.expat
import webapp.c_utilities as c
from os.path import *
import turbogears
import glob
import sys
import os
import re

if exists('song.db'):
  os.system('rm song.db')
  print '\nREMOVED EXISTING DATABASE\n'
 
os.system('tg-admin -c prod.cfg sql create')

if exists(join(dirname(__file__), "setup.py")):
  turbogears.update_config(configfile="dev.cfg",
    modulename="webapp.config")

# grab all songs and songbooks from directories
songlist = glob.glob('songs/*')
songbooklist = glob.glob('songbooks/*')

# enter songs into database
hub.begin() #open connection to database

print '\n'

for song in songlist:
  print 'Song:', song
  path = song
  try:
    dom = ET.parse(path)

    if dom.find('stitle') != None and dom.find('stitle').text != None:    #don't die if no title
      title = dom.find('stitle').text
    else:
      title = 'No title'
      print 'NO TITLE:', path

    if dom.find('author') != None and dom.find('author').text != None:    #don't die if no author
      author = dom.find('author').text
    else:
      author = ''

    if dom.find('categories') != None and dom.find('categories').text != None:    #don't die if no categories
      categories = dom.find('categories').text
    else:
      categories = ''

    #this code is direct copy from db.py song_save
    if dom.find('chunk/line') != None: #don't die if no content
      content = ''
      for line in dom.findall('chunk/line'):
        content += re.sub('<c.*?c>', '', ET.tostring(line).replace('<line>',' ').replace('</line>',' '))
    else:
      content = ''

  except xml.parsers.expat.ExpatError:
    title = 'No title'
    author = ''
    categories = ''
    print 'MALFORMED:', path
  
  Song(title=c.fix_encoding(title), path=path, author=c.fix_encoding(author), 
      categories=c.fix_encoding(categories), content=c.fix_encoding(content))
  hub.commit() #commit song to database

# enter songbooks into database
for songbook in songbooklist:
  if songbook.endswith('.comment') or songbook.endswith('.comment.dat') or songbook.endswith('.comment.dir') or songbook.endswith('.bak'):
    continue  # .comment files are not songbooks
 
  print 'Songbook:', songbook

  path = songbook

  try:
    dom = ET.parse(path)

    if dom.find('title') != None:    #don't die if no title
      title = dom.find('title').text
    else:
      print 'NO TITLE:', path
      title = 'No title'

  except xml.parsers.expat.ExpatError:
    title = 'No title'
    print 'MALFORMED:', path

  Songbook(title=c.fix_encoding(title), path=path)
  hub.commit()  #commit songbook to database

hub.end() #end connection to database

