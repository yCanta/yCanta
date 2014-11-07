from model import Song, Songbook
import elementtree.ElementTree as ET 
import mono2song
import cherrypy
import turbogears
import pdfformatter as formatter
import cssparser
from elementtree.ElementTree import parse
from elementtree.ElementTree import SubElement
import xml.sax.saxutils
import time
import os
import os.path
import re
import convert

BASE_PATH = cherrypy.config.get('song_base_path', '')
ALL_SONGS_PATH = "songbooks/all.xml"
TIME_FORMAT = "%a, %d %b %Y, %I %p"
TIME_ZONE = "US/Eastern"
UPLOAD_FILE = "Upload File"
BATCH_FILE_UPLOAD = "Upload Archive"
IMPORT_FROM_URL = "Import from URL"

def URL(url):
  if url.startswith('/'):
    return BASE_PATH + url
  return url

def pathcheck(path):
  "Raises a redirect if the path is bad"
  
  # allow empty paths
  if not path or not path.replace('#', '').strip():
    return

  # we check to see if the user is trying to hack us with a bad path
  if not path.startswith('song')  \
      or '..' in path \
      or '$' in path \
      or '~' in path:
    turbogears.flash('Bad path! "%s"' %path)
    raise cherrypy.HTTPRedirect(URL('/'))


def convertfile(filename):
  """Returns a dictionary as documented in convert/__init__.py"""

  ext = filename.split('.')[-1]

  conversion_func = convert.converter_for_fileext[ext]

  return conversion_func(filename)

def converturl(url):
  """Returns a dictionary as documented in convert/__init__.py"""

  import urlparse
  domain = urlparse.urlparse(url).hostname

  conversion_func = convert.converter_for_url[domain]

  return conversion_func(url)


def convertbatch(fileobject, filename, categories):
  ext = filename.split('.')[-1]
  convert.batch_converter_for_fileext[ext](fileobject, categories)


# path is path to songbook, save_name is the name that the config should be saved under
def save_config(path, save_name, config_string):
  songbook_xml = parse(path)

  config_section = songbook_xml.find('configuration')

  # create the config section if we must
  if config_section is None:
    config_section = SubElement(songbook_xml.getroot(), 'configuration')

  # search for formatter config section named save_name
  formatter_node = None
  for node in config_section.findall('formatter'):
    if node.get('name').lower().strip() == save_name.lower().strip():
      formatter_node = node
      break # we found our formatter node

  if formatter_node is None: # didn't find existing formatter_node
    formatter_node = SubElement(config_section, 'formatter')
    formatter_node.set('name', save_name.strip())

  # now we have a formatter node
  formatter_node.text = config_string

  # now save back to file
  songbook_xml.write(path)


def grab_title(song_content):
  for line in song_content.splitlines():
    if (line.find('<title>') != -1) & (line.find('</title>') != -1):
      title = line.replace('<title>', '').replace('</title>', '')
      break
    else:
      title = "No entered title"

  return title

def export2pdf(path, wpath, stylesheet):
  css = cssparser.CSS(stylesheet)
  pdf = formatter.parse(path, css)
  formatter.format(pdf, 'webapp/static/%s' % wpath, css)
  return 

def fix_encoding(text):
  if type(text) == unicode:
    return text.encode('utf-8', 'replace')
  else:
    return unicode(text, 'utf-8', 'replace').encode('utf-8', 'replace')

def not_error(item):
  try:
    Song.byPath(str(item.attrib['ref']))
    return 1
  except:
    turbogears.flash("Missing one or more songs, last missing song: " + item.attrib['ref'].replace('songs/','') + ' . . - song(s) not loaded')
    return 0
