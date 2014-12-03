#!/usr/bin/env python
import os
import re
import sys
import signal
import os.path

convert_dir = os.path.abspath(os.path.dirname(__file__))

def convert(input):
  d = {}                               # Define dictionary
  """ convert input file into dictionary as documented in __init__.py """
  # read content from file
  ss_content = open(input,'rU').read().splitlines()
 
  # split content into parts
  for item in ss_content:
    if item.lower().startswith('title'):
      d['title'] = item.replace('Title=','')

    elif item.lower().startswith('author'): 
      d['author'] = item.replace('Author=','').replace('|',',')
    elif item.lower().startswith('fields'):
      t = item.replace('Fields=','').lower()
      t = re.sub('[ ]*(\d)*','', t)
      d['chunk_type'] = t.rstrip('/t').split('/t')
    elif item.lower().startswith('words'):
      d['chunks'] = item.replace('Words=','').rstrip('/t').replace('/n','\n').split('/t')
    elif item.lower().startswith('copyright'):
      d['copyright'] = item.replace('Copyright=','')
    elif item.lower().startswith('[s'):
      d['cclis'] = item.replace('[S','').replace(']','').strip()
    elif item.lower().startswith('themes'):
      d['categories'] = item.replace('Themes=','').split('/t')

    else: 
      continue

  return d

if __name__ == '__main__':
  import sys
  d = convert(sys.argv[1])

   # write the song:
  print d['title']
  print '-'*len(d['title'])
  print
  print 'Author:', d['author']
  print
  for chunk in d['chunks']:
    print chunk
    print

