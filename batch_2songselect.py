import elementtree.ElementTree as ET 
import webapp.controllers as w
import webapp.c_utilities as c
from webapp.c_utilities import pathcheck
import turbogears
import glob
import sys
import os

turbogears.update_config(configfile=sys.argv[2], modulename="webapp.config")

folder = glob.glob(sys.argv[1] + '*' + '.usr')

for file in folder:
  print file 

  d = c.convertfile(file) # dictionary of content 
    
  os.system('rm -rf %s' % dir)

  chunklist = []
  c_type = d['chunk_type']

  i = 0
  for chunk in d['chunks']:
#    s_chunk = ET.Element("chunk")
#    s_chunk.text = chunk

    # set type
#    if 'chorus' in c_type[i].lower():
#      s_chunk.set('type', 'chorus')
#    elif 'bridge' in c_type[i].lower():
#      s_chunk.set('type', 'bridge')
#    else:
#      s_chunk.set('type', 'verse')

    chunklist.append(chunk)
    i = i+1

  #title
  if 'title' in d:
    title = d['title']
  else:
    title = ''
  #author
  if 'author' in d:
    author = d['author']
  else:
    author = ''
  #copyright
  if 'copyright' in d:
    copyrights = d['copyright']
  else:
    copyrights = ''
  #introduction
  if 'introduction' in d:
    introduction = d['introduction']
  else:
    introduction = ''
  if 'cclis' in d:
    cclis = d['cclis']
  else: 
    cclis = ''
  if 'categories' in d:
    categories = d['categories']
  else: 
    categories = ''


  c.song_save(title, author, introduction, copyrights, c_type, chunklist, 'path to song', categories, cclis, 'Save', 'True')




