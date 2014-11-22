# -*- coding: utf-8 -*-
import os
import re
import cgi
import glob
import time
import shelve
import dumbdbm
import whichdb
import mono2song
import xml.sax.saxutils
import xml.parsers.expat
import webapp.c_utilities as c
try: # try c version for speed then fall back to python
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET
from webapp.model import Song, Songbook, User, bootstrap_model

ALL_SONGS_PATH = "songbooks/all.xml"

def initialize_db():
  bootstrap_model()

def num_users_defined():
  return User.select().count()

def create_user(username, password):
  User(user_name=username, display_name=username, email_address="a@b", password=password)

def songs():
  songs = [songs for songs in Song.select(orderBy=Song.q.title)]
  songs.sort(key=lambda x: x.title.lower() or 'No Title')
  return songs

def songbooks():
  songbooks = [songbooks for songbooks in Songbook.select(orderBy=Songbook.q.title)]
  songbooks.sort(key=lambda x: x.title.lower() or 'No Title')
  
  # save and the remove the all songs songbook from the songbook list
  for i in range(len(songbooks)):
    if songbooks[i].path == ALL_SONGS_PATH:
      del songbooks[i]
      break # we found it and removed it -- done.
  return songbooks

def sync_songs():
  songlist = glob.glob('songs/*')

  for song in songlist:
    #print 'Song:', song
    path = song
    try:
      if Song.byPath(path): #skip existing songs in the db
        continue
    except:
      pass #song not found, error thrown, lets add it to the db!
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

def sync_songbooks():
  songbooklist = glob.glob('songbooks/*')
  for songbook in songbooklist:
    if songbook.endswith('.comment') or songbook.endswith('.comment.dat') or songbook.endswith('.comment.dir') or songbook.endswith('.bak'):
      continue  # .comment files are not songbooks
    #print 'Songbook:', songbook
    path = songbook
    try:
      if Songbook.byPath(path): #skip existing songbooks in the db
        continue
    except:
      pass #songbook not found, error thrown, lets add it to the db!
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

def save_song(title, author, scripture_ref, introduction, key,
    copyrights, path, cclis, submit, new, types, chunk_list, categories):
    
  if 0 and submit == "Cancel":
      turbogears.flash("Cancelled!")
      raise cherrypy.HTTPRedirect(URL("/"))

  else:
    # make sure lists are lists not strings
    if isinstance(categories, basestring):
      categories = [categories]
    if isinstance(chunk_list, basestring):
      chunk_list = [chunk_list]
    if isinstance(types, basestring):
      types = [types]

    if title.strip() == '':
      title = 'New Song'
    
    title = re.sub(r'(^|[\s\-)(\\\/]\b)(\S)', lambda m: m.group(1) + m.group(2).upper(), title)

    chunk_list = [c.fix_encoding(chunk) for chunk in chunk_list]
    categories = [c.fix_encoding(category) for category in categories if category.strip()]
    types      = [c.fix_encoding(typ.lower()) for typ in types]               #lowering case because edit is upper
 
    cat_str = ', '.join(categories)

    if new == True:
      path = c.gen_unique_path('songs/%s.song', title, author)
      assert not os.path.exists(path)
      c.pathcheck(path)
      song = Song(title=c.fix_encoding(title), path=path, author=c.fix_encoding(author), 
          categories=c.fix_encoding(cat_str), content='')

    else:
      # we check to see if the user is trying to hack us with a bad path
      c.pathcheck(path)
      song = Song.byPath(str(path))

      # check if title or author is changed, if yes change and rename it, also update links in songbooks
      if song.title != title or song.author != author:
        song.title = c.fix_encoding(title)  # update title if needed
        song.author = c.fix_encoding(author)
        old_path = os.path.normpath(path)
        new_path = os.path.normpath(c.gen_unique_path('songs/%s.song', title, author))
        os.rename(old_path,new_path)
        path = new_path
        song.path = path

        #rename old_path occurences in all of the songbooks
        songbook_paths = Songbook.select()
        for songbook in songbook_paths:
          if songbook.path == c.ALL_SONGS_PATH:  # Don't bother with all songs songbook
            continue

          sb = open(songbook.path, "rU").read()
          if old_path in sb:
            open(songbook.path, 'w').write(sb.replace(old_path, new_path))
            
            sb_comment = get_comment_db(songbook.path)
            if sb_comment.has_key(str(old_path)):
              comment = sb_comment[str(old_path)]
              del sb_comment[str(old_path)]
              sb_comment[str(new_path)] = comment
              sb_comment.close()  # save our changes


      song.categories = c.fix_encoding(cat_str)
      song.content = ''

        #0------------------------------------------------
   
    root = ET.Element("song")
    root.set("format-version", "0.1")

    s_title = ET.SubElement(root,"stitle")
    s_title.text = title or ' '
    s_author = ET.SubElement(root,"author")
    s_author.text = author
    s_scripture_ref = ET.SubElement(root,"scripture_ref")
    s_scripture_ref.text = scripture_ref
    s_introduction = ET.SubElement(root,"introduction")
    s_introduction.text = introduction
    s_key = ET.SubElement(root,"key")
    s_key.text = key
    s_categories = ET.SubElement(root,"categories")
    s_categories.text = cat_str 
    s_cclis = ET.SubElement(root,"cclis")
    s_cclis.text = cclis
    
    split_chunk = 0
    i = 0 #counter for chunk_list
    while(i<len(chunk_list)):
      #split at blank lines with no following text 
      new_chunks = re.split('\n[ \t\r\f\v]*?\n(?=\s*?\S)', chunk_list[i])
      if new_chunks[0] != chunk_list[i]:
        split_chunk = 1
        chunk_list.pop(i)
        chunk_list = chunk_list[:i] + new_chunks + chunk_list[i:]
        n=1
        while (n < len(new_chunks)):
          types.insert(i,types[i])
          n += 1
        i += len(new_chunks)
      else:
        i += 1 
    
    i = 0 
    for chunk in chunk_list:
      s_chunk = ET.Element("chunk")
      s_chunk.set("type", types[i])
      lines = chunk.splitlines()
      n = 0
      while n < len(lines):
        # if it looks like a chord line and the next line doesn't ... then treat it as a chord line
        if (n+1 < len(lines)) and mono2song.is_chord(lines[n]) and not mono2song.is_chord(lines[n+1]):
          line = '<line>' + mono2song.combine(lines[n],lines[n+1]) + '</line>'
          try:
            s_chunk.append(ET.fromstring(line))
          except:
            print 'ERROR!!', '\n'*2, lines[n]
            print lines[n+1]
            print 'OUT:', line, '\n'*2
            raise
          n += 2
        elif lines[n].strip() != '':
          line = '<line>' + xml.sax.saxutils.escape(lines[n]) + '</line>'
          s_chunk.append(ET.fromstring(line))
          n += 1
        else:
          n += 1
          
      root.append(s_chunk)
      i = i + 1

    # add copyright information to the element tree
    s_copyright = ET.SubElement(root, "copyright")
    copyrights = copyrights.replace('(c)',u'©').replace('(C)',u'©')

    s_copyright.text = copyrights

    tree = ET.ElementTree(root)
    tree.write(path)
    
    # now update/create new song entry in database

    #this code is direct copy from regen_db.py
    if root.find('chunk/line') != None: #don't die if no content
      content = ''
      for line in root.findall('chunk/line'):
        content += re.sub('<c.*?c>', '', ET.tostring(line).replace('<line>',' ').replace('</line>',' '))
    else:
      content = ''

    
  #  Now that we have parsed the content we can update it in the database
  song.content = c.fix_encoding(content)

  return [split_chunk, path]

def songbooks_containing_song(path):
  #check to make sure not in any songbooks
  songbook_paths = Songbook.select()
  
  songbooks = [] 
  for songbook in songbook_paths:
    if songbook.path != c.ALL_SONGS_PATH and path in open(songbook.path, "rU").read():
      songbooks.append(songbook)

  return songbooks

def do_delete_file(path):
  del_path = os.path.join('deleted', path)
  del_dir = os.path.dirname(del_path)

  if not os.path.exists(del_dir):
    os.makedirs(del_dir)

  os.rename(path, del_path)

def delete_song(path):

  conflict_songbooks = ', '.join([songbook.title for songbook in songbooks_containing_song(path)])

  if conflict_songbooks != '':
    return conflict_songbooks

  if os.access(path, os.W_OK):
    do_delete_file(path)
  song = Song.byPath(str(path))
  song.destroySelf()
  return conflict_songbooks

def delete_songbook(path):
  if os.access(path, os.W_OK):
    do_delete_file(path)

  com_path = os.path.splitext(path)[0] + '.comment'
  com_files = glob.glob(com_path+'*')
  for f in com_files:
    do_delete_file(f)

  songbook = Songbook.byPath(str(path))
  songbook.destroySelf()
  return

def rename_st_category(category, new_category):
  category = category.strip()
  new_category = new_category.strip()

  all_songs = songs()
  modified_songs = [] 
  
  # update the categories file
  categories = open('song_categories').read()
  categories = [c.strip() for c in categories.split(',')]

  def rename_category(categories, category, new_category):
    updated_categories = []
    for cat in categories:
      if category.strip() == cat.strip():
        cat = new_category
      updated_categories.append(cat.strip())

    text = ', '.join(updated_categories)
    return text

  open('song_categories','w').write(rename_category(categories, category, new_category))

  # update all the songs in the database
  for song in all_songs:
    try:
      if category in song.categories: #we may have found a song with the category
        song_xml = ET.parse(song.path)
        categories = song_xml.find('categories')
        if categories is None:
          continue
        
        old_cat = categories.text
        categories.text = rename_category(categories.text.split(','), category, new_category)
        if old_cat != categories.text:
          # update the database
          song.categories = categories.text 
          # write changes to song file
          song_xml.write(song.path)
          modified_songs.append(song.title)
    except:
      continue
  return modified_songs 

def get_st_categories():
  try:
    st_categories = open('song_categories').read()
    st_categories = [c.strip() for c in st_categories.split(',')]
    return st_categories
  except IOError:
    return []

def get_comment_db(songbook_path):
  # check if this is the All songs songbook, if so don't do anything
  if songbook_path == c.ALL_SONGS_PATH:
    return dict()

  comment_path = os.path.splitext(songbook_path)[0] + '.comment'

  # check if this is an old comment file -- we now use dumbdbm for portability
  # upgrade done automatically TODO: this could be removed in the future
  if whichdb.whichdb(comment_path) != 'dumbdbm':
    # get a copy of the comments
    old_shelf = shelve.open(comment_path)
    comments = dict(old_shelf)
    old_shelf.close()

    # remove the old database file
    files = glob.glob(comment_path+'*')
    for f in files:
      os.remove(f)

    # write comments into dumbdbm shelf
    new_shelf = shelve.Shelf(dumbdbm.open(comment_path))
    for k in comments.keys():
      new_shelf[k] = comments[k]
    new_shelf.close()  # close to make sure .comment file saved

  # now assured of a dumbdbm shelf
  return shelve.Shelf(dumbdbm.open(comment_path))

def get_comments(songbook_path):
  return dict(get_comment_db(songbook_path))

 
def save_comment(songbook_path, song, commenter, comment):
  # get the comment file as shelf object for this songbook (if it does not exist it is created)
  sb_comment = get_comment_db(songbook_path)
  
  # format the comment
  formatted_comment = '<div><b>'+cgi.escape(commenter)+'</b>'+time.strftime(" (%A, %b %d, %I:%M %p, %Y):")+'<pre>'+cgi.escape(comment)+'</pre></div>'

  # add new comment, properly formatted, to the comments for 'song'
  if str(song) in sb_comment:
    sb_comment[str(song)] += formatted_comment
  else:
    sb_comment[str(song)] = formatted_comment

  # save comment to return
  comment_result = sb_comment[str(song)]

  # close/save comment file
  sb_comment.close()

  return comment_result

def add_category(cat_text):
  categories = open('song_categories', 'a')
  categories.write(', '+cat_text)
  categories.close()

  return cat_text
