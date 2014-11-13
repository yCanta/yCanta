import turbogears
from model import Song, Songbook#, hub
from c_utilities import pathcheck, URL
from docutils.core import publish_parts
import cherrypy
from cherrypy import request
import re
from sqlobject import SQLObjectNotFound
from turbogears import validators, controllers, expose, flash, identity, redirect, visit
import song2mono, mono2song
import db
import c_utilities as c 
import time
import os
import os.path
import hashlib
import glob
import tempfile
try: # try c version for speed then fall back to python
  import xml.etree.cElementTree as ET
  from xml.etree.cElementTree import parse
except ImportError:
  import xml.etree.ElementTree as ET
  from xml.etree.ElementTree import parse
import types
import pdfformatter as formatter
import commands

#base_path = cherrypy.config.get('song_base_path', '')
SONG_BACKUP_PATH = cherrypy.config.get('SONG_BACKUP_PATH', 'song_backup')
SONGBOOK_BACKUP_PATH = cherrypy.config.get('SONGBOOK_BACKUP_PATH', 'songbook_backup')

if cherrypy.config.get('song_cd_to', ''):
  os.chdir(cherrypy.config.get('song_cd_to'))

if cherrypy.config.get('song_path', ''):
  if 'PATH' in os.environ:
    os.environ['PATH'] = os.environ['PATH'] + ':' + cherrypy.config.get('song_path')
  else:
    os.environ['PATH'] = cherrypy.config.get('song_path')

refresh_time = int(cherrypy.config.get('song_refresh', '0'))

version =  os.popen('git show -s --format="git:%h"').read().strip() or 'hg:' + os.popen('hg id -i').read().strip()

class Root(turbogears.controllers.RootController):
  @turbogears.expose(template="webapp.templates.index")
  def default(self, path):
    return self.index()

  @turbogears.expose(template="webapp.templates.index")
  def index(self):
    if db.num_users_defined() == 0: # first run ...
      redirect(URL("/first_run"))

    return dict(songbooks=db.songbooks()) 

  @turbogears.expose(template="webapp.templates.first_run")
  def first_run(self):
    if db.num_users_defined() != 0:
      turbogears.flash('Not the first run.  User already defined.')
      redirect(URL('/'))

    db.initialize_db()   
    db.sync_songs()
    db.sync_songbooks()

    return dict(songbooks=[])

  @turbogears.expose()
  def create_user(self, username, password, verify, go):
    print 'USER:', username, password, verify, go
    if password != verify:
      turbogears.flash('Passwords don\'t match.  Try again.')
      redirect(URL('/first_run'))

    db.create_user(username, password)
    redirect(URL('/'))

  @turbogears.expose(template="webapp.templates.reload")
  def reload(self):
    return dict(time=refresh_time)

  @turbogears.expose(format="json")
  @identity.require(identity.not_anonymous())
  def songs_list(self):
    songs=db.songs()
    out = ""
    for song in songs:
      out += "<a href=\"song_view#path=" + song.path + "\">" + song.title + "</a>"
    return out 
 
  @turbogears.expose()
  @identity.require(identity.not_anonymous())
  def delete(self, path):
    pathcheck(path)
    if path.startswith('songs'):
      result = db.delete_song(path)

      if result != '':
        turbogears.flash("This song cannot be deleted as it is in the following songbooks:" + result)
        raise cherrypy.HTTPRedirect(URL("/song_view#path=%s" % path))
      else:
        turbogears.flash("Song Deleted!")
        raise cherrypy.HTTPRedirect(URL("/song_view#"))    

    elif path.startswith('songbooks'):
      db.delete_songbook(path)
      raise cherrypy.HTTPRedirect(URL("/"))
    else:
      raise cherrypy.HTTPRedirect(URL("/"))
  
  @turbogears.expose()
  @identity.require(identity.not_anonymous())
  def save_comment(self, songbook_path, song, commenter, comment):
    pathcheck(songbook_path)
    return db.save_comment(songbook_path, song, commenter, comment)

  @turbogears.expose()
  @identity.require(identity.not_anonymous())
  def add_category(self, cat_text):
    return db.add_category(cat_text)

  @turbogears.expose(format="json")
  @identity.require(identity.not_anonymous())
  def rename_category(self, categories):
    categories = categories.split(',')
    if len(categories) == 2:
      out = db.rename_st_category(categories[0], categories[1])
      return 'Modified: ' + ', '.join(out)
    elif len(categories) > 2:
      return "Too many ','s in you list"
    return 'Rename failed'

  @turbogears.expose(format="json")
  @identity.require(identity.not_anonymous())
  def song_view_content(self, path):
    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)
    
    try:
      song = Song.byPath(str(path))
    except SQLObjectNotFound:
      raise cherrypy.HTTPRedirect(URL("/notfound?path=%s" % path))

    songXML = open(song.path).read()
    return songXML
 
  @turbogears.expose(format="json")
  @identity.require(identity.not_anonymous())
  def song_information(self, path):
    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)
    
    songbooks_containing = '<br />'.join([songbook.title for songbook in db.songbooks_containing_song(path)])
    songbooks_containing = []
    for songbook in db.songbooks_containing_song(path):
      songbooks_containing.append('<a href="'+URL('/songbook_view?path='+songbook.path)+'">'+songbook.title+'</a>')

    songbooks_containing = '<br />'.join(songbooks_containing)
    
    if songbooks_containing == '':
      information = '<b>Not used in any songbook</b>'
    else:
      information = '<b>Used in:</b><br />'+songbooks_containing

    return information

  @turbogears.expose(template="webapp.templates.song_view")
  @identity.require(identity.not_anonymous())
  def song_view(self, path="songs/jesujesu.son"):
    # we check to see if the user is trying to hack us with a bad path
    #pathcheck(path)
    
    def song_title(f):
      try:
        return Song.byPath(str(f)).title, 
      except SQLObjectNotFound:
        return '[SONG NOT IN DATABASE -- REPORT THIS]'

    recent_list = ((os.path.getmtime('songs/'+f), 'songs/'+f) for f in os.listdir('songs/'))
    
    sorted_list = sorted(recent_list, reverse=True)[:15]

    # look up song title from database last for efficency (10 lookups vs 1 for every song the entire db)
    sorted_list = [(t[0], song_title(t[1]), t[1]) for t in sorted_list]

   # print 40*'\n',sorted_list

    return dict(recent_updates=sorted_list, songs_list=db.songs(), songbooks=db.songbooks())
 
  @turbogears.expose(template="webapp.templates.song_edit")
  @identity.require(identity.not_anonymous())
  def song_edit(self, path):

    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)

    song = Song.byPath(str(path))
    path = song.path
    song_xml = ET.parse(path)

    # get information from song_xml
    title = 'Untitled' 
    author = ''
    scripture_ref =''
    intro = ''
    key = ''
    copyrights = ''
    cclis = None 
    categories = '' 

    if song_xml.find('stitle') != None:
      title = song_xml.find('stitle').text 
    if song_xml.find('author') != None:
      author = song_xml.find('author').text
    if song_xml.find('scripture_ref') != None:
      scripture_ref = song_xml.find('scripture_ref').text
    if song_xml.find('introduction') != None:
      intro = song_xml.find('introduction').text
    if song_xml.find('key') != None:
      key = song_xml.find('key').text
    if song_xml.find('copyright') != None:
      copyrights = song_xml.find('copyright').text
    if song_xml.find('cclis') != None:
      cclis = song_xml.find('cclis').text
    if song_xml.find('categories') != None and song_xml.find('categories').text != None:
      categories = [cat.strip() for cat in song_xml.find('categories').text.split(',')]

    chunks = song_xml.findall('chunk')

    for chunk in chunks:
      chunk_text=[]
      lines = chunk.findall('line')
      for line in lines:
        if song2mono.is_chord_line(ET.tostring(line))==1:
          chunk_text.append(song2mono.expand_chord(ET.tostring(line)))
        else:
          chunk_text.append(line.text or "")

      chunk.text = '\n'.join(chunk_text)

    return dict(title=title, author=author, scripture_ref=scripture_ref, introduction=intro, key=key, copyrights=copyrights, chunks=chunks, path=path, new=False, songbooks=db.songbooks(), cclis=cclis, categories=categories, def_title="New Song")
  
  @turbogears.expose()
  @turbogears.validate(validators=dict(new=validators.StringBoolean()))
  @identity.require(identity.not_anonymous())
  def song_save(self, title, author, scripture_ref, introduction, key, copyrights, path, submit, new, cclis=None, types=[], chunk_list=[], categories=[]):

    ret_status = db.save_song(title, author, scripture_ref, introduction, key, copyrights, path, cclis, submit, new, types, chunk_list, categories)

    #rdiff-backup
    os.system('rdiff-backup songs/ %s' % SONG_BACKUP_PATH)

    if ret_status[0] == 1:
      turbogears.flash("Changes saved! Please review chunk splits and types and save again to update.")
      raise cherrypy.HTTPRedirect(URL("/song_edit?path=%s" % ret_status[1])) 
    else:
      turbogears.flash("Changes saved!")
      raise cherrypy.HTTPRedirect(URL("/song_view#path=%s" % ret_status[1]))
  
  @turbogears.expose(template="webapp.templates.songbook_view")
  @identity.require(identity.not_anonymous())
  def songbook_view(self, path=c.ALL_SONGS_PATH):
    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)

    if path == c.ALL_SONGS_PATH:
      #create songbook all songs from scratch and save in location.  Then pass it to be viewed

      title = "All Songs"
      songbook_content = '''<songbook format-version="0.1">\n<title>''' + title.strip() + "</title>"

      #get all paths and sort them
      songs = [songs for songs in Song.select(orderBy=Song.q.title)]
      songs.sort(key=lambda x: x.title.lower() or 'No Title')
      
      for song in songs:
        songbook_content = songbook_content + '\n<songref ref="' + song.path +'" status="n"/>'
      
      songbook_content = songbook_content + '\n</songbook>'
      
      write = open(path, "w")
      write.write(songbook_content)
      write.close()
      
      try:
        all_songs_songbook = Songbook.byPath(str(path))
      except SQLObjectNotFound:
        all_songs_songbook = Songbook(title=title, path=str(path))

    try:
      if path != c.ALL_SONGS_PATH:
        #look up title from database
        songbook = Songbook.byPath(str(path))
        title = songbook.title
    except SQLObjectNotFound:
      raise cherrypy.HTTPRedirect(URL("/notfound?path=%s" % path))
    

    sb_xml = parse(path)

    #same as in songbook_edit below 
    item_els = sb_xml.getroot().getchildren()
    songbook_items=[]
    for item in item_els:
      if item.tag == 'songref':
        songbook_items.append((Song.byPath(str(item.attrib['ref'])).title, item.attrib['ref'], item.get('status','n')))
      if item.tag == 'section':
        songbook_items.append((item.attrib['title'],'','section'))

    return dict(title=title, path=path, songbook_items=songbook_items, songbooks=db.songbooks())
  
  @turbogears.expose(template="webapp.templates.songbook_edit")
  @identity.require(identity.not_anonymous())
  def songbook_edit(self, path):

    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)

    songbook = Songbook.byPath(str(path))
    path = songbook.path
    songbook_content = open(songbook.path, "rU").read()
    title = c.grab_title(songbook_content)
    sb_xml = parse(songbook.path)

    #same as in songbook_view above
    item_els = sb_xml.getroot().getchildren()
    songbook_items=[]
    for item in item_els:
      if item.tag == 'songref':
        songbook_items.append((Song.byPath(str(item.attrib['ref'])).title, item.attrib['ref'], item.get('status','n')))
      if item.tag == 'section':
        songbook_items.append((item.attrib['title'],'','section'))

    password = ''
    if sb_xml.find('password') != None:
      password = sb_xml.find('password').text 

    return dict(title=title, path=path, new=False, songs_list=db.songs(), songbooks=db.songbooks(), songbook_items=songbook_items, password=password, def_title="New Songbook")
  
  
  @turbogears.expose()
  @turbogears.validate(validators=dict(new=validators.StringBoolean()))
  @identity.require(identity.not_anonymous())
  def songbook_save(self, title, path, submit, new, password, songbook_items=[], status=[]):
#    turbogears.flash("1: '%s'" % (songbook_items))
    if 0 and submit == "Cancel":
      turbogears.flash("Cancelled!")
      raise cherrypy.HTTPRedirect(URL("/"))
    else:
      #hub.begin()
      #title = c.grab_title(songbook_content) May need to replace this line with something to grab a new title when the title is changed
      if title.strip() == '':
        title = 'New Songbook'

      if new == True:
        path = 'songbooks/%s-%s.xml' % (time.time(), 
          re.sub('[^a-z0-9]+', '-', title.lower()) )
        assert not os.path.exists(path)
        pathcheck(path)
        
        songbook = Songbook(title=title, path=path)
      else:
        # we check to see if the user is trying to hack us with a bad path
        pathcheck(path)
        songbook = Songbook.byPath(str(path))
        songbook.title = title  # update title if needed
       
      songbook_content = '''<songbook format-version="0.1">\n<title>''' + title.strip() + "</title>"

      # make sure songbook_items is a list not a string
      if isinstance(songbook_items, basestring):
        songbook_items = [songbook_items]
      if isinstance(status, basestring):
        status = [status]
     
      # counter for accessing status for each element
      s = 0  
      for item in songbook_items:
        if status[s] != 'section':
          songbook_content = songbook_content + '\n<songref status="' + status[s] + '" ref="' + item +'"/>'
        elif status[s] == 'section':
          songbook_content += '\n<section title="' + item + '"/>'
        s += 1
      

      #preserve configuration settings
      config_string = ''  # sane default config
      try:
        song_xml_config = ET.parse(path).find('configuration')
        if song_xml_config:
          config_string = ET.tostring(song_xml_config)
      except IOError:
        pass  # do nothing here -- config_string default previously defined
      if password.strip() != '':
        songbook_content += '\n<password>' + password + '</password>'
      songbook_content = songbook_content + '\n' + config_string
      songbook_content = songbook_content + '</songbook>'
      
      
      write = open(path, "w")
      write.write(songbook_content)
      write.close()
      #hub.commit()
      #hub.end()

      #rdiff-backup

      os.system('rdiff-backup songbooks/ %s' % SONGBOOK_BACKUP_PATH)

      turbogears.flash("Changes saved!")
      raise cherrypy.HTTPRedirect(URL("/songbook_view?path=%s" % path))
  
  @turbogears.expose(template="webapp.templates.song_edit")
  @identity.require(identity.not_anonymous())
  def create_song(self):
    return dict(title="New Song", author='', scripture_ref='', introduction='', key='',  copyrights='', 
        chunks=[ET.Element('chunk')], path="path to song", new=True, 
        cclis=None, categories='',  songbooks=db.songbooks(), def_title="New Song")
  
  @turbogears.expose(template="webapp.templates.songbook_edit")
  @identity.require(identity.not_anonymous())
  def create_songbook(self):
    return dict(title="New Songbook", path="path to songbook", new=True,
        songbook_items="", songs_list=db.songs(), songbooks=db.songbooks(),
        password='', def_title="New Songbook")
  
  @turbogears.expose(template="webapp.templates.upload_form")
  @identity.require(identity.not_anonymous())
  def upload_form(self, path="songs/jesujesu.son"):
    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)
    
    return dict(songbooks=db.songbooks())

  @turbogears.expose(template="webapp.templates.export_form")
  @identity.require(identity.not_anonymous())
  def export_form(self, path="songs/jesujesu.son", selected="simple.cfg"):
    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)
    
    try:
      if 'songbook'in path:
        exportS = Songbook.byPath(str(path))
      elif 'song' in path:
        exportS = Song.byPath(str(path))
      else:
        raise cherrypy.HTTPRedirect(URL("/notfound?path=%s" % path))


    except SQLObjectNotFound:
      raise cherrypy.HTTPRedirect(URL("/notfound?path=%s" % path))
    title = exportS.title

    cf_dir = "config_files/"
    # grab all the paths for the config files
    config_paths = glob.glob(cf_dir + "*")
    config_files = dict()

    # for loop reads stylesheets and packages them in a list of dictionaries
    for c_path in config_paths:
      tmp_dict = dict()
      # read path and dump contents in tmp

      for line in open(c_path, "rU"):
        line = line.replace('--','').replace('-','_').split()
        if len(line) == 2:
          tmp_dict[line[0]]=line[1].replace('_','-')

      #config_files[c_path.replace(cf_dir,'')]=tmp_dict
      config_files[os.path.basename(c_path)]=tmp_dict

    songbook_configs = dict()
    songbook_xml = parse(path)
    for format_config in songbook_xml.findall('//formatter'):
      key = format_config.get('name')
      config_val = dict()

      # parse the config_val dict from the xml element content
      raw_args = format_config.text.replace('--', '').replace('-', '_').split()
      for i in range(0, len(raw_args), 2):
        if i+1 < len(raw_args): # can't go out of bounds
          config_val[raw_args[i]] = raw_args[i+1].replace('_', '-')

      # lets store this key and config
      songbook_configs[key] = config_val
    # done parsing songbook_configs

    #DEBUG:  print config_files
    return dict(title=title, path=path, config_files=config_files, songbook_configs=songbook_configs, songbooks=db.songbooks(), selected=selected)

  @turbogears.expose(template="webapp.templates.song_edit")
  @identity.require(identity.not_anonymous())
  def upload(self, upload, submit, categories='', **keywords):
    try:
      # have a URL to import
      if submit == c.IMPORT_FROM_URL:
        d = c.converturl(upload)

      # uploaded file
      elif submit == c.UPLOAD_FILE:
        data = upload.file.read()

        dir = tempfile.mkdtemp() 
        target_file_name = os.path.join(dir, upload.filename)

        f = open(target_file_name, 'wb')
        f.write(data)
        f.close()
        
        d = c.convertfile(target_file_name) # dictionary of content 
        
        os.system('rm -rf %s' % dir)

        #turbogears.flash("File uploaded successfully: %s saved as: %s" % (upload.filename, target_file_name))

      elif submit == c.BATCH_FILE_UPLOAD:
        c.convertbatch(upload.file, upload.filename, [cat.strip() for cat in categories.split(',')])
        raise cherrypy.HTTPRedirect(URL('/'))

      else: # what to do here?
        print 1/0 # XXX: error handling needed

      chunklist = []
      c_type = d['chunk_type']

      i = 0
      for chunk in d['chunks']:
        s_chunk = ET.Element("chunk")
        s_chunk.text = chunk

        # set type
        if 'pre-chorus' in c_type[i].lower():
          s_chunk.set('type', 'pre-chorus')
        elif 'chorus' in c_type[i].lower():
          s_chunk.set('type', 'chorus')
        if 'final chorus' in c_type[i].lower():
          s_chunk.set('type', 'final chorus')
        elif 'no label' in c_type[i].lower():          
          s_chunk.set('type', 'no label')
        elif 'bridge' in c_type[i].lower():
          s_chunk.set('type', 'bridge')
        elif 'ending' in c_type[i].lower():
          s_chunk.set('type', 'ending')
        else:
          s_chunk.set('type', 'verse')

        chunklist.append(s_chunk)
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
      #scripture reference
      if 'scripture_ref' in d:
        scripture_ref = d['scripture_ref']
      else:
        scripture_ref = ''
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
      #key
      if 'key' in d:
        key = d['key']
      else:
        key = ''
      #cclis
      if 'cclis' in d:
         cclis = d['cclis']
      else:
         cclis = None 
      #categories (of worship)
      if 'categories' in d:
         categories = d['categories']
      else:
         categories = ''

      return dict(title=title, author=author, scripture_ref=scripture_ref, introduction=introduction, key=key, copyrights=copyrights, cclis=cclis, categories=categories, chunks=chunklist,path='path to song', new=True, songbooks=db.songbooks(), def_title="New Song")

    except:
      turbogears.flash('The upload/import encountered an error.  Please verify the file extension or website address is supported.')
      raise cherrypy.HTTPRedirect(URL('/upload_form'))
   

  @turbogears.expose(template="webapp.templates.raw_edit")
  @identity.require(identity.not_anonymous())
  def raw_edit(self, path, redir_path=URL('/')):

    # we check to see if the user is trying to hack us with a bad path
    pathcheck(path)


    if os.path.exists(path):
      raw_content = open(path, "rU").read() 
    else:
      raw_content = "Replace this text with your song categories.\nEach category separated by a comma."
     
    return dict(path=path, raw_content=raw_content, songbooks=db.songbooks(), redir_path=redir_path)
        
  
  @turbogears.expose()
  @identity.require(identity.not_anonymous())
  def raw_save(self, raw_content, path, submit, redir_path=URL('/')):
    pathcheck(path)
    write = open(path, "w")
    write.write(raw_content)
    write.close()

    turbogears.flash("Changes saved!")
    if path.startswith('songs'):
      raise cherrypy.HTTPRedirect(URL("/song_view#path=%s" % path))
    elif path.startswith('songbooks'):
      raise cherrypy.HTTPRedirect(URL("/songbook_view?path=%s" % path))
    else: 
      raise cherrypy.HTTPRedirect(URL('/'+redir_path))

  
  @turbogears.expose()
  @identity.require(identity.not_anonymous())
  def export2pdf(self, path, config_file, save_name, submit_export=0, save_config=0, print_a=0, print_n=0, print_r=0, **args):
   #  we check to see if the user is trying to hack us with a bad path
   #print path
   pathcheck(path)

   #print repr(args)

   #-----------need to handle possible missing info------------------
   #
   #
   #
   #
   #-----------------------------------------------------------------

   arguments = ""
   #format arguments
   for k in args:
     # if the argument was left empty -- we can't have that because the parser
     # will get messed up and pick the next argument as the value (ex. "--font
     # --foo" is parsed as the font argument == --foo)
     if not args[k].strip():
       args[k] = 'None'
     arguments += '--' + k.replace('_', '-') + ' ' + args[k] + ' '

   #Configures which songs to print based on status
   songs_to_print = '' 
   print_status_args = ''
   if print_a:
     songs_to_print += 'a'
     print_status_args += '--print_a checked '
   if print_n:
     songs_to_print += 'n'
     print_status_args += '--print_n checked '
   if print_r:
     songs_to_print += 'r'
     print_status_args += '--print_r checked '
   if songs_to_print == '':
     songs_to_print = 'anr'
   
   
   if save_config:
     c.save_config(path, save_name, arguments + print_status_args)
     raise cherrypy.HTTPRedirect(URL("/export_form?path=%s&selected=%s" % (path, save_name)))

   arguments += '--songs-to-print ' + songs_to_print + ' '

   wpath = re.sub('[.].*$','', path) + '.pdf' 

   # create a hash of the songbook and arguments -- if either changes we want a new path to the PDF
   book_arg_hash = hashlib.md5()
   book_arg_hash.update(open(path).read())
   book_arg_hash.update(arguments)
   book_arg_hash = book_arg_hash.hexdigest()     # get a string of the hash

   dir, fn = os.path.split(wpath)                # split into dir and file
   wpath = '%s/%s/%s' % (dir, book_arg_hash, fn) # add the hash as the last directory

   # create book_arg_hash dir if needed
   if not os.path.isdir('webapp/static/%s/%s' % (dir, book_arg_hash)):
     os.makedirs('webapp/static/%s/%s' % (dir, book_arg_hash))        

   #print path, wpath
   formatter.format2pdf(path, 'webapp/static/' + wpath, arguments)

   raise cherrypy.HTTPRedirect(URL("/static/%s" % wpath))

  @turbogears.expose(template="webapp.templates.songbook_export2html")
  @identity.require(identity.not_anonymous())
  def export2html(self, path, secondary="false"):
    #only load songs if there is a need to
    if secondary == "false":
      # we check to see if the user is trying to hack us with a bad path
      pathcheck(path)
      
      try:
        songbook = Songbook.byPath(str(path))
        title=songbook.title
      except SQLObjectNotFound:
        raise cherrypy.HTTPRedirect(URL("/notfound?path=%s" % path))

      #get list of refs from file
      sb_xml = ET.parse(path)
      songref_els = sb_xml.findall('songref')
      songref_refs = [item.attrib['ref'] for item in songref_els]
      
      #converted html variable
      songbook_html = '<div class="booktitle">' + sb_xml.find('title').text + '</div>'

      #for loop to parse all songs and combine into songbook xml
      for ref in songref_refs:
        songbook_html += open(ref).read()

    else:
      title = "Presentation"
      songbook_html = ""

    f = open('webapp/static/javascript/jquery-1.9.1.min.js')
    jQuery = f.read()
    f.close()

    f = open('webapp/static/javascript/presentation.js')
    presentation = f.read()
    f.close()

    return dict(songbook_html=songbook_html, title=title, jQuery=jQuery, presentation=presentation, secondary=secondary)
   
  @turbogears.expose(template="webapp.templates.index")
  def notfound(self, path):
    turbogears.flash("Invalid path or link")
    raise cherrypy.HTTPRedirect(URL("/"))

  @expose(template="webapp.templates.login")
  def login(self, forward_url=None, *args, **kw):
      """Show the login form or forward user to previously requested page."""

      if forward_url:
          if isinstance(forward_url, list):
              forward_url = forward_url.pop(0)
          else:
              del request.params['forward_url']

      new_visit = visit.current()
      if new_visit:
          new_visit = new_visit.is_new

      if (not new_visit and not identity.current.anonymous
              and identity.was_login_attempted()
              and not identity.get_identity_errors()):
          redirect(forward_url or '/', kw)

      if identity.was_login_attempted():
          if new_visit:
              msg = _(u"Cannot log in because your browser "
                       "does not support session cookies.")
          else:
              msg = _(u"The credentials you supplied were not correct or "
                       "did not grant access to this resource.")
      elif identity.get_identity_errors():
          msg = _(u"You must provide your credentials before accessing "
                   "this resource.")
      else:
          msg = _(u"Please log in.")
          if not forward_url:
              forward_url = request.headers.get("Referer", "/")

      # we do not set the response status here anymore since it
      # is now handled in the identity exception.
      return dict(logging_in=True, message=msg,
          forward_url=forward_url, previous_url=request.path_info,
          original_parameters=request.params, songbooks=db.songbooks())

  @expose()
  def logout(self):
      """Log out the current identity and redirect to start page."""
      identity.current.logout()
      redirect(URL("/"))
