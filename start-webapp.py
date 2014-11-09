#!/usr/bin/python
import pkg_resources
pkg_resources.require("TurboGears")

import turbogears
import cherrypy
cherrypy.lowercase_api = True

from os.path import *
import os
import sys

for i in range(len(sys.argv)):
  if sys.argv[i] == '--start-browser':
    del sys.argv[i]
    start_browser = True

# first look on the command line for a desired config file,
# if it's not on the command line, then
# look for setup.py in this directory. If it's not there, this script is
# probably installed
if len(sys.argv) > 1:
    turbogears.update_config(configfile=sys.argv[1], 
        modulename="webapp.config")
elif exists(join(dirname(__file__), "setup.py")):
    turbogears.update_config(configfile="dev.cfg",
        modulename="webapp.config")
else:
    turbogears.update_config(configfile="prod.cfg",
        modulename="webapp.config")

import os
if os.name == 'nt':
  print 'OS', os.name
  dburi = turbogears.config.get('sqlobject.dburi')
  print 'DBURI', dburi
  dburi = 'sqlite:///' + os.path.abspath(dburi.replace('sqlite://', '')).replace(':', '|')
  print 'DBURI', dburi
  dburi = turbogears.config.update({'sqlobject.dburi': dburi})

import os.path
if not os.path.exists('songs'):
  os.mkdir('songs')

if not os.path.exists('songbooks'):
  os.mkdir('songbooks')

if start_browser:
  import webbrowser
  webbrowser.open('http://127.0.0.1:8880')

from webapp.controllers import Root

turbogears.start_server(Root())
