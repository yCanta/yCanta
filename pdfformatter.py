#!/usr/bin/env python
import os.path

import re
import string

try: # try c version for speed then fall back to python
  from xml.etree.cElementTree import Element
  from xml.etree.cElementTree import parse as etree_parse
except ImportError:
  from xml.etree.ElementTree import Element
  from xml.etree.ElementTree import parse as etree_parse

import reportlab.lib.pagesizes
from reportlab.pdfgen import canvas
from reportlab.lib.units import toLength, inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from optparse import OptionParser

try:
    from collections import defaultdict
except:
    class defaultdict(dict):
        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                not hasattr(default_factory, '__call__')):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)
        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value
        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()
        def copy(self):
            return self.__copy__()
        def __copy__(self):
            return type(self)(self.default_factory, self)
        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(self.items()))
        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))


INDENT_NO_LABEL = 'indented no label'
VARIABLE_INDENT = ('verse', 'no label', INDENT_NO_LABEL, 'introduction')
SCRIPTURE_IN_TITLE    = 'in-title'
SCRIPTURE_UNDER_TITLE = 'under-title'
INDEX_ON_NEW_PAGE     = 'on-new-page'
INDEX_NO_PAGE_BREAK   = 'no-page-break'
INDEX_OFF             = 'no-index'
BIBLE_BOOK_ORDER_DICT = {'gen':1,'genesis':1,'ex':2,'exod':2,'exodus':2,'lev':3,'leviticus':3,'num':4,'numbers':4,'deut':5,'deuteronomy':5,'josh':6,'joshua':6,'judg':7,'judges':7,'ruth':8,'ruth':8,'1 sam':9,'1 samuel':9,'2 sam':10,'2 samuel':10,'1 kings':11,'1 kings':11,'2 kings':12,'2 kings':12,'1 chr':13,'1 chron':13,'1 chronicles':13,'2 chr':14,'2 chron':14,'2 chronicles':14,'i sam':9,'i samuel':9,'ii sam':10,'ii samuel':10,'i kings':11,'i kings':11,'ii kings':12,'ii kings':12,'i chron':13,'i chronicles':13,'ii chron':14,'ii chronicles':14,'ezra':15,'ezra':15,'neh':16,'nehemiah':16,'esth':17,'esther':17,'job':18,'job':18,'ps':19,'psalm':19,'psalms':19,'prov':20,'proverbs':20,'eccles':21,'ecclesiastes':21,'song of sol':22,'song of solomon':22,'isa':23,'is':23,'isaiah':23,'jer':24,'jeremiah':24,'lam':25,'lamentations':25,'ezek':26,'ezekiel':26,'dan':27,'daniel':27,'hos':28,'hosea':28,'joel':29,'joel':29,'amos':30,'amos':30,'obad':31,'obadiah':31,'jon':32,'jonah':32,'mic':33,'micah':33,'nah':34,'nahum':34,'hab':35,'habakkuk':35,'zeph':36,'zephaniah':36,'hag':37,'haggai':37,'zech':38,'zechariah':38,'mal':39,'malachi':39,'matt':40,'mt':40,'matthew':40,'mk':41,'mark':41,'lk':42,'luke':42,'jn':43,'john':43,'act':44,'acts':44,'rom':45,'romans':45,'1 cor':46,'1 corinthians':46,'i cor':46,'i corinthians':46,'2 cor':47,'2 corinthians':47,'ii cor':47,'ii corinthians':47,'gal':48,'galatians':48,'eph':49,'ephesians':49,'phil':50,'philippians':50,'col':51,'colossians':51,'1 thess':52,'1 thessalonians':52,'i thess':52,'i thessalonians':52,'2 thess':53,'2 thessalonians':53,'ii thess':53,'ii thessalonians':53,'1 tim':54,'1 timothy':54,'2 tim':55,'2 timothy':55,'i tim':54,'i timothy':54,'ii tim':55,'ii timothy':55,'tit':56,'titus':56,'philem':57,'philemon':57,'heb':58,'hebrews':58,'jas':59,'james':59,'1 pet':60,'1 peter':60,'2 pet':61,'2 peter':61,'1 john':62,'1 john':62,'2 john':63,'2 john':63,'3 john':64,'3 john':64,'i pet':60,'i peter':60,'ii pet':61,'ii peter':61,'i john':62,'i john':62,'ii john':63,'ii john':63,'iii john':64,'iii john':64,'jude':65,'jude':65,'rev':66,'revelation':66}

# ================
# our data objects
# ================
class Songbook(object):
  def __init__(self, title, ccli=''):
    self.title = title
    self.ccli = ccli
    self.songs = []
    self.scrip_index = ScripIndex() # list of IndexEntry's
    self.index = Index()            # list of IndexEntry's
    self.cat_index = CatIndex()     # dict of CatIndexEntry's
    self.height = 0
    self.height_after = 0

class Index(list):
  def __init__(self, *args, **vargs):
    list.__init__(self, *args, **vargs)
    self.height = 0
    self.height_after = 0

class ScripIndex(list):
  def __init__(self, *args, **vargs):
    list.__init__(self, *args, **vargs)
    self.height = 0
    self.height_after = 0

class CatIndex(defaultdict):
  def __init__(self, *args, **vargs):
    defaultdict.__init__(self, list, *args, **vargs)
    self.height = 0
    self.height_after = 0

class Category(object):
  def __init__(self, category, height):
    self.category = category
    self.height = height
    self.height_after = 0

class IndexEntry(object):
  def __init__(self, song, index_text, is_song_title):
    self.song = song
    self.index_text = index_text.strip()
    self.is_song_title = is_song_title
    self.height = 0
    self.height_after = 0

class CatIndexEntry(IndexEntry):
  pass

class Song(object):
  def __init__(self, title, author, copyright='', ccli='', scripture_ref='', key='', introduction=None, categories=None):
    self.title = title.strip()
    self.author = author.strip()
    self.copyright = copyright.strip()
    self.ccli = ccli.strip()
    self.scripture_ref = scripture_ref.strip()
    self.key = key.strip()
    if self.key:
      self.key = 'Key: ' + self.key
    self.introduction = introduction
    self.categories = categories or list()

    self.chunks = []
    self.num = None  # song number in songbook
    self.height = 0
    self.height_after = 0

class Chunk(object):
  def __init__(self, type):
    self.type = type
    self.lines = []
    self.num = None # verse number if self.type == 'verse' else None
    self.height = 0
    self.height_after = 0

  def has_chords(self):
    return len([l for l in self.lines if l.chords]) != 0

class Line(object):
  def __init__(self, text, chords):
    self.text = text
    self.chords = chords
    self.height = 0
    self.height_after = 0

def sort_scrip_index(scrip_ref): 
  x = re.split('\s(?=\d)', scrip_ref.strip().replace('.',''), 1)
  
  # get the book number XX
  try:
    book_number = str(BIBLE_BOOK_ORDER_DICT[x[0]])
  except:
    book_number = '99'
  book_number = book_number.zfill(2)
  
  # get chapter number YYY
  try:
    chapter_number = x[1].split(':')[0]
  except:
    chapter_number = '000'
  if len(chapter_number) < 4:
    chapter_number = chapter_number.zfill(3)
  else:
    chapter_number = '999'

  # get verse number ZZZ
  try:
    verse_number = re.split('[-,]',x[1].split(':')[1])[0]
    verse_number = verse_number.zfill(3)
    if len(verse_number) > 3:
      verse_number = '000'
  except:
    verse_number = '000'
 
  return book_number + chapter_number + verse_number

def parse_song(song_xml):
  title = song_xml.find('stitle')
  if title is not None:  # if not found title is None
    title = title.text or 'Untitled'
  else:
    title = 'Untitled'

  author = song_xml.find('author')
  if author is not None:  # if not found author is None
    author = author.text or ''
  else:
    author = ''

  categories = song_xml.find('categories')
  if categories is not None and categories.text is not None:  # if not found categories is None
    categories = [c.strip() for c in categories.text.split(',')]
  else:
    categories = []

  ccli = song_xml.find('cclis')
  if ccli is not None:
    ccli = ccli.text or ''
  else:
    ccli = ''

  copyright = song_xml.find('copyright')
  if copyright is not None:
    copyright = copyright.text or ''
  else:
    copyright = ''

  scripture_ref = song_xml.find('scripture_ref')
  if scripture_ref is not None:
    scripture_ref = scripture_ref.text or ''
  else:
    scripture_ref = ''

  key = song_xml.find('key')
  if key is not None:
    key = key.text or ''
  else:
    key = ''

  intro = song_xml.find('introduction')
  if intro is not None:
    intro = intro.text or ''
  else:
    intro = ''

  song = Song(title, author, copyright=copyright, ccli=ccli, scripture_ref=scripture_ref, key=key, introduction=intro.strip(), categories=categories)

  # parse song chunks
  verse_num = 1
  for chunk_xml in song_xml.findall('chunk'):
    type=chunk_xml.attrib['type']
    chunk = Chunk(type)
    
    # skip comment chunks
    if chunk.type == 'comment':
      continue
    # increment verse count
    elif chunk.type == 'verse':
      chunk.num = verse_num
      verse_num += 1

    # parse lines and chords in chunk
    for line in chunk_xml.findall('line'):
      text = line.text or ''
      chords = {}

      # parse chords and rest of line text
      for c in line.findall('c'):
        chords[len(text)] = c.text # len(text) is offset in text where chord appears
        text += c.tail or ''

      # done parsing line -- add it
      line = Line(text, chords)
      chunk.lines.append(line)

    # done parsing chunk -- add it
    song.chunks.append(chunk)

  return song


def parse(xml, cfg):
  # if xml passed as filename, convert to object
  if isinstance(xml, basestring) and os.path.isfile(xml):
    xml = etree_parse(xml).getroot()

  # check if we are parsing a song and not a songbook
  if xml.tag == 'song':
    song = parse_song(xml)
    song.num = 1
    return song


  # Ok we are doing a songbook
  # ==========================

  # parse songbook information
  title = xml.find('title').text

  songbook = Songbook(title)

  song_num = 1
  # iterate through all songs in the songbook
  for songref in xml.findall('songref'):
    song_xml = etree_parse(songref.attrib['ref'])
    
    if(songref.get('status') not in cfg.SONGS_TO_PRINT):
      continue

    song = parse_song(song_xml)
    song.num = song_num
    song_num += 1

    # done parsing song -- add it
    songbook.songs.append(song)

    # generate index entries for this song
    if cfg.DISPLAY_INDEX != INDEX_OFF:
      songbook.index.append(IndexEntry(song, song.title, is_song_title=True))
    for cat in song.categories:  # an entry for each category in the song
      exclude = False
      for exc in cfg.INDEX_CAT_EXCLUDE:
        if re.search(exc, cat): # cat matches exclusion
          exclude = True
          break
      if not exclude:
        songbook.cat_index[cat].append(CatIndexEntry(song, song.title, is_song_title=True))

    # add entries for scripture ref
    if song.scripture_ref and cfg.DISPLAY_SCRIP_INDEX != INDEX_OFF:
      scripture_refs = re.split('[,;]\s(?=[A-Za-z])',song.scripture_ref)
      for scripture_ref in scripture_refs:
        songbook.scrip_index.append(IndexEntry(song, scripture_ref, is_song_title=True))

    # add some first line index entries
    if cfg.INCLUDE_FIRST_LINE and cfg.DISPLAY_INDEX != INDEX_OFF:
      first_verse = True
      for chunk in song.chunks:
        # if this is a chorus chunk or a first verse chunk AND the first line is not the same as the song title
        if ((chunk.type == 'chorus' or (chunk.type in ('verse', 'no label', INDENT_NO_LABEL) and first_verse))
            and len(chunk.lines) > 0 and re.sub(r'[^A-Za-z]', '', chunk.lines[0].text).lower() != re.sub(r'[^A-Za-z]', '', song.title).lower()):

          songbook.index.append(IndexEntry(song, chunk.lines[0].text, is_song_title=False))
          # TODO? at the moment, not including first line entries in cat index

          # don't do any more verse index entries -- we aren't on the first verse anymore
          if chunk.type in ('verse', 'no label', INDENT_NO_LABEL):
            first_verse = False

    # done with index


  # done parsing songbook -- return
  return songbook


class PageMapping:
  def __init__(self, page=None, startx=None, starty=None, endx=None, endy=None):
    assert page is not None and startx is not None and starty is not None and endx is not None and endy is not None
    self.page = page
    self.startx = startx
    self.starty = starty
    self.endx = endx
    self.endy = endy

class PageLayout(object):
  """Interface required for objects doing page layout and ordering"""
  def __init__(self, options):
    pass

  def get_page_width(self):
    '''Returns the width of each page (not piece of paper) based on the options passed to __init__'''
    pass

  def get_page_height(self):
    '''Returns the height of each page (not piece of paper) based on the options passed to __init__'''
    pass

  def page_order(self, pages):
    '''Returns a list of lists -- each inner list maps 0..n virtual pages to the physical paper'''
    pass

  def previous_page_visible(self, previous_pages):
    '''Returns True or False -- looks at previous_pages to determine if the chorus needs to be duplicated'''
    pass

page_layouts = {}
def register_page_layout(name, klass):
  assert name not in page_layouts
  page_layouts[name] = klass

def get_page_layouts():
  return page_layouts.keys()

class PageLayoutSimple(PageLayout):
  def __init__(self, options):
    self.cfg = options

  def get_page_width(self):
    return self.cfg.PAPER_WIDTH - (self.cfg.PAPER_MARGIN_RIGHT + self.cfg.PAPER_MARGIN_LEFT
                                  +self.cfg.PAGE_MARGIN_RIGHT  + self.cfg.PAGE_MARGIN_LEFT)

  def get_page_height(self):
    return self.cfg.PAPER_HEIGHT - (self.cfg.PAPER_MARGIN_TOP + self.cfg.PAPER_MARGIN_BOTTOM
                                   +self.cfg.PAGE_MARGIN_TOP  + self.cfg.PAGE_MARGIN_BOTTOM)

  def page_order(self, pages):
    cfg = self.cfg
    # helper function
    def _make_mapping(p):
      return PageMapping(
          page=p,
          startx=cfg.PAPER_MARGIN_LEFT+cfg.PAGE_MARGIN_LEFT,
          starty=cfg.PAPER_HEIGHT-(cfg.PAPER_MARGIN_TOP+cfg.PAGE_MARGIN_TOP),
          endx=cfg.PAPER_WIDTH-(cfg.PAPER_MARGIN_RIGHT+cfg.PAGE_MARGIN_RIGHT),
          endy=cfg.PAPER_MARGIN_BOTTOM+cfg.PAGE_MARGIN_BOTTOM)

    return [[_make_mapping(p)] for p in pages]

  def previous_page_visible(self, previous_pages):
    return False 

#register_page_layout('simple', PageLayoutSimple)

class PageLayoutColumn(PageLayout):
  def __init__(self, options):
    self.cfg = options

  def get_page_width(self, margin=1):
    ret = (self.cfg.PAPER_WIDTH - (self.cfg.PAPER_MARGIN_RIGHT + self.cfg.PAPER_MARGIN_LEFT)) / self.cfg.COLUMNS
    if margin:
      ret = ret - (self.cfg.PAGE_MARGIN_RIGHT + self.cfg.PAGE_MARGIN_LEFT)
    return ret

  def get_page_height(self):
    return self.cfg.PAPER_HEIGHT - (self.cfg.PAPER_MARGIN_TOP + self.cfg.PAPER_MARGIN_BOTTOM
                                   +self.cfg.PAGE_MARGIN_TOP  + self.cfg.PAGE_MARGIN_BOTTOM)

  def page_order(self, pages):
    ret = []
    curent_paper_page = []
    
    for p in pages:
      sx=self.cfg.PAPER_MARGIN_LEFT+self.cfg.PAGE_MARGIN_LEFT + len(curent_paper_page)*self.get_page_width(margin=0)
      sy=self.cfg.PAPER_HEIGHT - (self.cfg.PAPER_MARGIN_TOP + self.cfg.PAGE_MARGIN_TOP)
      ex=sx + self.get_page_width(margin=1) # margin=1 so margins not included in calc
      ey=self.cfg.PAPER_MARGIN_BOTTOM + self.cfg.PAGE_MARGIN_BOTTOM

      curent_paper_page.append(PageMapping(page=p, startx=sx, starty=sy, endx=ex, endy=ey))
      
      if len(curent_paper_page) >= self.cfg.COLUMNS:
        ret.append(curent_paper_page)
        curent_paper_page = []

    if len(curent_paper_page) > 0:
      ret.append(curent_paper_page)

    return ret

  def previous_page_visible(self, previous_pages):
    # if the previous_pages just completed the last column on the previous physical page
    if len(previous_pages) % self.cfg.COLUMNS == 0:
      return False

    return True  

#register_page_layout('column', PageLayoutColumn)


def shift_mappings(mappings, right=0):
  '''Helper function to shift pagemappings left-right'''
  for map in mappings:
    map.startx += right
    map.endx   += right

  return mappings


class PageLayoutColumn1Sided(PageLayoutColumn):
  def __init__(self, options):
    PageLayoutColumn.__init__(self, options)

    # save old width and apply binder
    self.old_width = self.cfg.PAPER_WIDTH
    self.cfg.PAPER_WIDTH = self.old_width - self.cfg.BINDER_MARGIN

  def page_order(self, pages):
    pages = PageLayoutColumn.page_order(self, pages)
    for pg in  pages:
      shift_mappings(pg, right=self.cfg.BINDER_MARGIN)

    # return page size to normal
    self.cfg.PAPER_WIDTH = self.old_width

    return pages

register_page_layout('single-sided', PageLayoutColumn1Sided)


class PageLayoutColumn2Sided(PageLayoutColumn):
  def __init__(self, options):
    PageLayoutColumn.__init__(self, options)

    # save old width and apply binder
    self.old_width = self.cfg.PAPER_WIDTH
    self.cfg.PAPER_WIDTH = self.old_width - self.cfg.BINDER_MARGIN

  def page_order(self, pages):
    pages = PageLayoutColumn.page_order(self, pages)
    for i,pg in enumerate(pages):
      if i % 2 == 0:  # every other page must be shifted since we are printing double sided
        shift_mappings(pg, right=self.cfg.BINDER_MARGIN)

    # return page size to normal
    self.cfg.PAPER_WIDTH = self.old_width

    return pages

register_page_layout('double-sided', PageLayoutColumn2Sided)


class PageLayoutBooklet(PageLayoutColumn):
  def __init__(self, options):
    PageLayoutColumn.__init__(self, options) # call super

    # mess with paper size -- make it half size with new height being old width and new width being 1/2 old height
    # we won't keep this messed up size, but it is needs to be messed up prior to the formatting stage
    self.old_width = self.cfg.PAPER_WIDTH
    self.old_height = self.cfg.PAPER_HEIGHT
    self.cfg.PAPER_HEIGHT = self.old_width
    self.cfg.PAPER_WIDTH = (self.old_height - self.cfg.BINDER_MARGIN) / 2.0 

  def page_order(self, pages):
    # first run through our parent (column layout) page order algorithm
    pages = PageLayoutColumn.page_order(self, pages)
    
    # now pages is a list of lists of PageMappings -- we need to map 4 of the inner lists onto each sheet of paper
    paper_pages = []
    # page mapping in booklet is: page4 and page1 on one side of a sheet of paper and page2 and page3 on the otherside
    #
    #  (outside sheet)      (inside sheet)
    # +---------------+    +---------------+
    # |       |       |    |       |       |
    # | Page4 | Page1 |    | Page2 | Page3 |
    # |       |       |    |       |       |
    # +---------------+    +---------------+
    # 

    page1 = []
    page2 = []
    page3 = []
    page4 = []

    # process pages in groups of 4
    for i in range(0, len(pages), 4):
      if (i+0) < len(pages) :  # page 1 on physical paper
        page1 = shift_mappings(pages[i+0], right=self.cfg.PAPER_WIDTH + self.cfg.BINDER_MARGIN)  # shift right (include binder)
      if (i+1) < len(pages) :  # page 2 on physical paper
        page2 = pages[i+1]                                                   # no shift
      if (i+2) < len(pages) :  # page 3 on physical paper
        page3 = shift_mappings(pages[i+2], right=self.cfg.PAPER_WIDTH + self.cfg.BINDER_MARGIN)  # shift right (include binder)
      if (i+3) < len(pages) :  # page 4 on physical paper
        page4 = pages[i+3]                                                   # no shift

        # all 4 pages have now been found and shifted as needed
        paper_pages.append(page4+page1)  # 4 and 1 on same page
        paper_pages.append(page2+page3)  # 2 and 3 on following page
        
        # discard saved pages -- they are now in page list
        page1 = []
        page2 = []
        page3 = []
        page4 = []

    # add any pages that were defined but not added (adds only done in the loop when page 4 is reached)
    if page1:
      paper_pages.append(page1)
    if page2 or page3:
      paper_pages.append(page2+page3)

    # set the paper sizes back to normal (but flipped 90 degrees)
    self.cfg.PAPER_WIDTH = self.old_height
    self.cfg.PAPER_HEIGHT = self.old_width

    return paper_pages

  def previous_page_visible(self, previous_pages):
    # base our decision on what parent PageLayoutColumn would do
    crosses_pages =  PageLayoutColumn.previous_page_visible(self, previous_pages)

    # but we have page 2 and page 3 opening across from each other
    # and page 4 and 1 open across from each other when the little booklets go together
    # ... so in one case we can see previous page even when columns say we shouldn't
    physical_pages = len(previous_pages) / self.cfg.COLUMNS      # self.cfg.COLUMNS per page


    # if this is page 2 or 4 now, then prev. page is visible 
    if physical_pages % 4 in (2, 0):
      return True 
    
    # default -- do parent's decision
    return crosses_pages


register_page_layout('booklet', PageLayoutBooklet)


class PageLayoutAdobeBooklet(PageLayoutColumn):
  def __init__(self, options):
    PageLayoutColumn.__init__(self, options) # call super

    # mess with paper size -- make it half size with new height being old width and new width being 1/2 old height
    old_width = self.cfg.PAPER_WIDTH
    old_height = self.cfg.PAPER_HEIGHT
    self.cfg.PAPER_HEIGHT = old_width
    self.cfg.PAPER_WIDTH = old_height / 2.0

register_page_layout('adobe-booklet', PageLayoutAdobeBooklet)

def myStringWidth(text, font, size):
  s = stringWidth(text, font, size)
  return s

def word_wrap(text, width, font, size, hanging_indent=0):
  if isinstance(text,Line):
    Line_object = True
    orig_text = text   # save original line object
    chords = text.chords
    text = text.text
  else:    
    Line_object = False

  if text.strip() == '':
    return []
  """ Returns a list of strings that will fit inside width """
  out = []
  text = text.split(' ')
  while len(text) > 0:
    num_words = len(text)

    while num_words > 1 and myStringWidth(' '.join(text[:num_words]), font, size) > width:
      num_words = num_words - 1 # try again minus one word

    # num_words is now the most that can fit this line
    new_text = ' '.join(text[:num_words])
    del text[:num_words] # remove the text that is now in our output

    new_chords = {}

    if Line_object:
      for item in chords.keys():
        if item < len(new_text):
          new_chords[item] = chords[item]
          del chords[item]
      out.append(Line(new_text,new_chords))
      for item in chords.keys():
        chords[item - len(new_text)] = chords[item]
        del chords[item]

    else: #normal text
      out.append(new_text)

    # we just added the first line
    if len(out) == 1: 
      width -= hanging_indent

  return out

def print_chords(pdf, cfg=None, font_size=None, y_offset=None, x_offset=None, page_mapping=None, line=None):
  assert None not in (pdf, cfg, font_size, y_offset, x_offset, page_mapping, line)

  y_offset += cfg.SONGCHORD_SIZE
  pdf.setFont(cfg.FONT_FACE, cfg.SONGCHORD_SIZE)

  # loop through chords
  char_offsets = sorted(line.chords.keys())
  for char_offset in char_offsets:
    chord_offset = pdf.stringWidth(line.text[:char_offset], cfg.FONT_FACE, font_size)
    pdf.drawString(page_mapping.startx + x_offset + chord_offset, page_mapping.starty - y_offset, line.chords[char_offset])

  return y_offset + cfg.SONGCHORD_SPACE


def print_line(pdf, font_face=None, font_size=None, y_offset=None, x_offset=0, line_space=None, page_mapping=None, line=None):
  assert None not in (pdf, font_face, font_size, y_offset, line_space, page_mapping, line)

  y_offset += font_size

#DBG  # rect around text
#DBG  pdf.setStrokeColor('blue')
#DBG  pdf.rect(page_mapping.startx+x_offset, page_mapping.starty-y_offset,
#DBG      pdf.stringWidth(line, font_face, font_size), font_size, fill=False)
#DBG  # rect for line space
#DBG  pdf.setStrokeColor('green')
#DBG  pdf.setFillColor('green')
#DBG  pdf.rect(page_mapping.startx+x_offset, page_mapping.starty-(y_offset + line_space),
#DBG      pdf.stringWidth(line, font_face, font_size), line_space, fill=True)
#DBG  # big rect around everything
#DBG  pdf.setStrokeColor('red')
#DBG  pdf.rect(page_mapping.startx+x_offset, page_mapping.starty-(y_offset + line_space),
#DBG      pdf.stringWidth(line, font_face, font_size), font_size+line_space)
#DBG  # reset
#DBG  pdf.setStrokeColor('black')
#DBG  pdf.setFillColor('black')

  pdf.setFont(font_face, font_size)
  pdf.drawString(page_mapping.startx+x_offset, page_mapping.starty - y_offset, line)
  
  return y_offset + line_space

def page_height(p):
  return sum(i.height + i.height_after for i in p)

def paginate(songbook, cfg):
  ''' returns a list of pages: each page is a list of things to show on that page 
      Songbook and Song objects only count for titles and headers - chunks have to be listed separate

      *** calculations MUST be kept in sync with calc_heights and format_page
  '''

  def height_of_introduction_plus_first_chunk(chunks):
    height = 0
    for c in chunks:
      height += c.height
      if c.type != 'introduction':
        break

    return height

  USABLE_HEIGHT = cfg.PAPER_HEIGHT - (cfg.PAGE_MARGIN_BOTTOM + cfg.PAGE_MARGIN_TOP + cfg.PAPER_MARGIN_BOTTOM + cfg.PAPER_MARGIN_TOP)
  pages = []

  # we may be called with just a song and not a songbook
  if isinstance(songbook, Song):
    list_of_songs = [songbook]
    p = []
  else:
    list_of_songs = songbook.songs
    p = [songbook]

  songs_have_been_added = False

  for song in list_of_songs:
    # if cfg says each song on a new page and this isn't the first song in the book
    # or if we can't fit the song header and a non-intro chunk on the page go to the next page
    if cfg.START_SONG_ON_NEW_PAGE and songs_have_been_added \
        or page_height(p) + song.height + height_of_introduction_plus_first_chunk(song.chunks) > USABLE_HEIGHT:
      pages.append(p)
      p = [] # new page

    # song header will fit
    p.append(song)

    # now songs have been added :-)
    songs_have_been_added = True

    chorus = []
    # fit as many chunks as we can
    for idx,chunk in enumerate(song.chunks):
      # to maximize space usage we can usually subtract SONGLINE_SPACE because
      # we don't need it at the bottom of a page -- HOWEVER, if the last chunk
      # has copyright info, we can't remove SONGLINE_SPACE because it is not
      # at the bottom of the page
      if chunk.last_chunk: # last_chunk only set when there is copyright for the song
        songline_correct = 0
      else:
        songline_correct = cfg.SONGLINE_SPACE

      # this chunk doesn't fit -- next page 
      if page_height(p) + (chunk.height - songline_correct) > USABLE_HEIGHT:
        pages.append(p)
        p = [] # new page

        # duplicate the chorus on each new page/column/etc if the page layout says it is needed
        # Also ... if there are enough verses left in this song (i.e. > 1) then we want to dupe the chorus AFTER adding the verse
        if len(chorus) != 0 and not cfg.page_layout.previous_page_visible(previous_pages=pages):

          # this chunk and at least one more are still to go -- so do chunk, chorus, chunk... end-of-song
          # UNLESS this chunk is a chorus, in which case we want to print any pre-choruses first
          if idx+1 < len(song.chunks) and 'chorus' not in chunk.type:
            p.append(chunk)
            p.extend(chorus) # extend with chorus(es)
          else:  # this is the last chunk in the song -- do chorus, chunk, end-of-song
            p.extend(chorus) # extend with chorus(es)
            p.append(chunk)

        else: # no chorus stuff ... just add it 
          p.append(chunk)

      else: # space for this chunk
        p.append(chunk)

      if 'chorus' in chunk.type:
        chorus.append(chunk)

    # done with chunks in song -- on to next song

  # done with all songs in songbook -- add final song page if cat_index starts on next page and len(p) > 0
  if (cfg.DISPLAY_CAT_INDEX == INDEX_ON_NEW_PAGE):
    # Fresh page if current page has anything on it.
    if len(p) !=0:
      pages.append(p)
      p = []
    # add pages until previous page not visible so index is not visible from last song 
    while cfg.page_layout.previous_page_visible(pages):
      pages.append(p)
      p = []

  # now do category index pages if we are paginating a songbook
  if isinstance(songbook, Songbook) and cfg.DISPLAY_CAT_INDEX != INDEX_OFF:
    # create a new page if no room on current page
    if page_height(p) + songbook.cat_index.height > USABLE_HEIGHT:
      pages.append(p)
      p = []

    # add cat_index title to page
    p.append(songbook.cat_index)

    for cat in sorted(songbook.cat_index.keys()):
      if (page_height(p) + songbook.cat_index.cat_height + songbook.cat_index[cat][0].height) > USABLE_HEIGHT:  # can't fit category + one index entry
        pages.append(p)
        p = []
      p.append(Category(cat, songbook.cat_index.cat_height))

      # sort cat_index entries then add to page
      entries = sorted(songbook.cat_index[cat], key=lambda m: re.sub(r'(?i)^([^a-z0-9]*the +|[^a-z0-9]+)', '', m.index_text.lower()))

      for index_entry in entries:
        # if there is no room for this entry, then the page is complete and we start a new one
        if (page_height(p) + index_entry.height) > USABLE_HEIGHT:
          pages.append(p)
          p = []

        # add the cat_index entry
        p.append(index_entry)
 
  # done with category index -- add last page if scripture index starts on next page and len(p) > 0
  if cfg.DISPLAY_SCRIP_INDEX == INDEX_ON_NEW_PAGE: 
    # Fresh page if current page has anything on it.
    if len(p) !=0:
      pages.append(p)
      p = []
    # add pages until previous index is not visible so index is not visible
    while cfg.page_layout.previous_page_visible(pages):
      pages.append(p)
      p = []

  # now do scripture index pages if we are paginating a songbook
  if isinstance(songbook, Songbook) and cfg.DISPLAY_SCRIP_INDEX != INDEX_OFF:
    # create a new page if no room on current page
    if page_height(p) + songbook.index.height > USABLE_HEIGHT:
      pages.append(p)
      p = []

    # add index title to page
    p.append(songbook.scrip_index)

    # sort index entries then add to page
    entries = sorted(songbook.scrip_index, key=lambda m: sort_scrip_index(re.sub(r'(?i)^([^a-z0-9]*the +|[^a-z0-9]+)', '', m.index_text.lower())))

    for index_entry in entries:
      # if there is no room for this entry, then the page is complete and we start a new one
      if (page_height(p) + index_entry.height) > USABLE_HEIGHT:
        pages.append(p)
        p = []

      # add the index entry
      p.append(index_entry)

  # done with scripture index -- add final page if index starts on next page and len(p) > 0
  if cfg.DISPLAY_INDEX == INDEX_ON_NEW_PAGE:
    # Fresh page if current page has anything on it.
    if len(p) !=0:
      pages.append(p)
      p = []
    # add pages until previous index is not visible so index is not visible
    while cfg.page_layout.previous_page_visible(pages):
      pages.append(p)
      p = []

  # now do regular index pages if we are paginating a songbook
  if isinstance(songbook, Songbook) and cfg.DISPLAY_INDEX != INDEX_OFF:
    # create a new page if no room on current page
    if page_height(p) + songbook.index.height > USABLE_HEIGHT:
      pages.append(p)
      p = []

    # add index title to page
    p.append(songbook.index)

    # sort index entries then add to page
    entries = sorted(songbook.index, key=lambda m: re.sub(r'(?i)^([^a-z0-9]*the +|[^a-z0-9]+)', '', m.index_text.lower()))

    for index_entry in entries:
      # if there is no room for this entry, then the page is complete and we start a new one
      if (page_height(p) + index_entry.height) > USABLE_HEIGHT:
        pages.append(p)
        p = []

      # add the index entry
      p.append(index_entry)

  # add final page (index or last song page if index is disabled)
  if len(p) != 0:
    pages.append(p)

  return pages


def calc_heights(songbook, cfg):
  """Calculates heights of songbook pieces -- calculations MUST be kept in sync with format_page and paginate"""
  # calc heights of elements and store in songbook object tree

  # we may be called with just a song even though the variable name suggests otherwise
  if isinstance(songbook, Song):
    list_of_songs = [songbook]
    index = []
    scrip_index = []
    cat_index = {}
  else:
    list_of_songs = songbook.songs 
    if not cfg.HIDE_BOOKTITLE:
      songbook.height = cfg.BOOKTITLE_SIZE + cfg.BOOKTITLE_SPACE
    else:
      songbook.height = 0

    # category index
    if cfg.DISPLAY_CAT_INDEX != INDEX_OFF:
      cat_index = songbook.cat_index
      songbook.cat_index.height = cfg.INDEX_TITLE_SIZE + cfg.INDEX_TITLE_SPACE
      songbook.cat_index.cat_height = cfg.INDEX_CAT_SIZE + cfg.INDEX_CAT_SPACE + cfg.INDEX_CAT_B4
    else:
      cat_index = {}

    # scripture index
    if cfg.DISPLAY_SCRIP_INDEX != INDEX_OFF:
      scrip_index = songbook.scrip_index
      songbook.scrip_index.height = cfg.INDEX_TITLE_SIZE + cfg.INDEX_TITLE_SPACE
      if cfg.DISPLAY_SCRIP_INDEX == INDEX_NO_PAGE_BREAK:  # only add space before if not starting on a new page
        songbook.scrip_index.height += cfg.INDEX_TITLE_B4
    else:
      scrip_index = [] # make scripture index height calculation loop be empty

    # index
    if cfg.DISPLAY_INDEX != INDEX_OFF:
      index = songbook.index
      songbook.index.height = cfg.INDEX_TITLE_SIZE + cfg.INDEX_TITLE_SPACE
      if cfg.DISPLAY_INDEX == INDEX_NO_PAGE_BREAK:  # only add space before if not starting on a new page
        songbook.index.height += cfg.INDEX_TITLE_B4
    else:
      index = [] # make index height calculation loop be empty


  for song in list_of_songs:
    song.height = 0

    if cfg.SCRIPTURE_LOCATION == SCRIPTURE_IN_TITLE and song.scripture_ref:
      song_title = cfg.SONGTITLE_FORMAT.safe_substitute(num=song.num, title=song.title + ' (%s)' % song.scripture_ref)
    else:
      song_title = cfg.SONGTITLE_FORMAT.safe_substitute(num=song.num, title=song.title)

    song.num_width = myStringWidth(cfg.SONGTITLE_FORMAT.safe_substitute(num=song.num, title=''), cfg.FONT_FACE, cfg.SONGTITLE_SIZE)*1.5

    # Word wrap title as needed
    song.title_wrapped = word_wrap(song_title, width=cfg.page_layout.get_page_width(),
        font=cfg.FONT_FACE, size=cfg.SONGTITLE_SIZE, hanging_indent=song.num_width)
    # add to height for each line
    song.height += sum(cfg.SONGTITLE_SIZE + cfg.SONGTITLE_SPACE for line in song.title_wrapped)

    # small text that goes under the title
    small_text = []
    if song.author:
      small_text.append(song.author)

    if cfg.SCRIPTURE_LOCATION == SCRIPTURE_UNDER_TITLE and song.scripture_ref:
      small_text.append(song.scripture_ref)

    if song.key:
      small_text.append(song.key)

    # wrap small_text
    small_text = (' '*8).join(small_text)
    song.small_text = word_wrap(small_text, width=cfg.page_layout.get_page_width(),
        font=cfg.FONT_FACE, size=cfg.SMALL_SIZE, hanging_indent=0)
    # add height of wrapped small_text
    song.height += sum(cfg.SMALL_SIZE + cfg.SMALL_SPACE for line in song.small_text)

    # introduction if applicable -- not shown when chords are not shown
    if song.introduction and cfg.DISPLAY_CHORDS:
      song.height += cfg.SONGCHORD_SIZE + cfg.SONGCHORD_SPACE

    for chunk in song.chunks:
      chunk.last_chunk = False  # the real last chunk is set true after loop

      # when word wrapping lines we need to split so chunk.lines is right length.
      if cfg.RESIZE_PERCENT == 0:
        split_lines = []
        for line in chunk.lines:
          split_line = word_wrap(line, width=(cfg.page_layout.get_page_width() - myStringWidth('8)   ', cfg.FONT_FACE, 
            cfg.SONGLINE_SIZE)), font=cfg.FONT_FACE, size=cfg.SONGLINE_SIZE, hanging_indent=0) 
          #myStringWdith('8 is copied from format_page - keep them in sync 
          split_lines += split_line

        chunk.lines = split_lines

      chunk.height = cfg.SONGCHUNK_B4 + len(chunk.lines) * (cfg.SONGLINE_SIZE + cfg.SONGLINE_SPACE)
      if chunk.type not in VARIABLE_INDENT:                     # if not a verse, intro, or  unlabeled chunk, we put
        chunk.height += cfg.SONGLINE_SIZE + cfg.SONGLINE_SPACE  # Chorus, Pre-Chorus, Bridge, etc on a separate line

      # space for chords
      if cfg.DISPLAY_CHORDS and chunk.has_chords():
        chunk.height += len(chunk.lines) * (cfg.SONGCHORD_SIZE + cfg.SONGCHORD_SPACE)

      # set height on lines (currently unused?)
      for l in chunk.lines:
        l.height = cfg.SONGLINE_SIZE + cfg.SONGLINE_SPACE
        if cfg.DISPLAY_CHORDS and chunk.has_chords():
          l.height += cfg.SONGCHORD_SIZE + cfg.SONGCHORD_SPACE

    # after looping through chunks and setting their height, any copyright_footer height is added to the last chunk
    # no copyright_footer if no copyright
    if song.copyright:
      copyright_text = 'Copyright ' + song.copyright + '.'
      if song.ccli:
        copyright_text = copyright_text + '  Used By Permission. CCLI License #'+cfg.CCLI

      song.chunks[-1].last_chunk = True  # lets the formatter know to print the copyright_footer
      song.chunks[-1].copyright_footer = word_wrap(copyright_text, width=cfg.page_layout.get_page_width(),
                                                   font=cfg.FONT_FACE, size=cfg.COPYRIGHT_SIZE)
      # add space for each line in copyright_footer
      song.chunks[-1].height += cfg.SONGCHUNK_B4 + sum(cfg.COPYRIGHT_SIZE + cfg.COPYRIGHT_SPACE
          for line in song.chunks[-1].copyright_footer)

    # end of song -- add SONG_SPACE_AFTER to last chunk (will be after the copyright) if there are chunks in song
    if len(song.chunks) > 0:
      song.chunks[-1].height_after = cfg.SONG_SPACE_AFTER

  
  # index
  for index_entry in index:
    if index_entry.is_song_title:
      index_entry.height = cfg.INDEX_SONG_SIZE + cfg.INDEX_SONG_SPACE
    else:
      index_entry.height = cfg.INDEX_FIRST_LINE_SIZE + cfg.INDEX_FIRST_LINE_SPACE

  # scrip index
  for index_entry in scrip_index:
    index_entry.height = cfg.INDEX_SONG_SIZE + cfg.INDEX_SONG_SPACE

  # cat index
  for c in cat_index:
    for index_entry in cat_index[c]:
      if index_entry.is_song_title:
        index_entry.height = cfg.INDEX_SONG_SIZE + cfg.INDEX_SONG_SPACE
      else:
        index_entry.height = cfg.INDEX_FIRST_LINE_SIZE + cfg.INDEX_FIRST_LINE_SPACE


def format_page(pdf, cfg, page_mapping):
  """Format a page onto the PDF -- calculations MUST be kept in sync with calc_heights and paginate"""

  # pick a standard indent that almost every chunk will fit (except for intros and probably verse 10 and greater)
  STANDARD_LABEL_INDENT_LENGTH = myStringWidth('8)   ', cfg.FONT_FACE, cfg.SONGLINE_SIZE)

  # REMEMBER: we are in the 1st Quadrant (like Math) ... lower left is (0,0)
  y = 0

  outline_level = 0

  # set clip region
  pdf.saveState() # so we can restore to no clip after this page

  if cfg.DEBUG_MARGINS:
    pdf.rect(page_mapping.startx, page_mapping.starty,
        page_mapping.endx-page_mapping.startx,page_mapping.endy-page_mapping.starty)

  # make a bounding box to keep from printing out of bounds
  p = pdf.beginPath()
  p.rect(page_mapping.startx, page_mapping.starty,
      page_mapping.endx-page_mapping.startx,page_mapping.endy-page_mapping.starty)
  pdf.clipPath(p, stroke=0)

  # draw page items
  for item in page_mapping.page:
    if isinstance(item, Songbook):
      # add to outline
      key = str(hash(('SONGBOOK ' + item.title)))
      pdf.bookmarkPage(key, left=page_mapping.startx, top=page_mapping.starty-y)
      outline_level = 0
      pdf.addOutlineEntry(item.title, key, level=outline_level)
      outline_level = 1

      # SONGBOOK TITLE
      if not cfg.HIDE_BOOKTITLE:
        y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.BOOKTITLE_SIZE, y_offset=y,
                        line_space=cfg.BOOKTITLE_SPACE, page_mapping=page_mapping, line=item.title)
    # SONG
    elif isinstance(item, Song):
      # add to outline
      key = str(hash('SONG(%d): %s' % (item.num, item.title)))
      pdf.bookmarkPage(key, left=page_mapping.startx, top=page_mapping.starty-y)
      pdf.addOutlineEntry(item.title, key, level=outline_level)
      #XXX: here we could add stuff to make index entries linkable

      # SONG TITLE
      for i, title_line in enumerate(item.title_wrapped):
        if i == 0: # first line
          indent = 0
        else:
          indent = item.num_width

        y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.SONGTITLE_SIZE, y_offset=y,
                        x_offset=indent, line_space=cfg.SONGTITLE_SPACE, page_mapping=page_mapping, line=title_line)

      # small_text after title
      for sm_line in item.small_text:
        y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.SMALL_SIZE, y_offset=y,
                       line_space=cfg.SMALL_SPACE, page_mapping=page_mapping, line=sm_line)

      # introduction if applicable -- not shown when chords are not shown
      if item.introduction and cfg.DISPLAY_CHORDS:
        y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.SONGCHORD_SIZE, y_offset=y,
                       line_space=cfg.SONGCHORD_SPACE, page_mapping=page_mapping, line=item.introduction)

    # VERSE OR CHORUS
    elif isinstance(item, Chunk):
      y += cfg.SONGCHUNK_B4

      # calulate prefix text for the chunk
      if item.type == 'chorus':
        label = 'Chorus:'
      elif item.type == 'verse':
        label = '%d)' % item.num
      elif item.type == 'bridge':
        label = 'Bridge:'
      elif item.type == 'pre-chorus':
        label = 'Pre-Chorus:'
      elif item.type == 'final chorus':
        label = 'Final Chorus:'
      elif item.type == 'ending':
        label = 'Ending:'
      elif item.type == 'introduction':
        label = 'Introduction:'
      else:
        label = ''


      if item.type in VARIABLE_INDENT:  # these chunks are indented by num of chars in label
        label_length = max(myStringWidth(label+'  ', cfg.FONT_FACE, cfg.SONGLINE_SIZE), STANDARD_LABEL_INDENT_LENGTH)
        # type indented no label gets an extra indent
        if item.type == INDENT_NO_LABEL:
          label_length *= 2
      else:                             # everything else gets a standard indent
        label_length = STANDARD_LABEL_INDENT_LENGTH

      # print the chunk lines
      if item.type == 'introduction' and not cfg.DISPLAY_CHORDS: # introduction is not shown when chords are not shown
        pass
      else:
        for count, line in enumerate(item.lines):
          if count == 0: # on the first line in the chunk write the label: chorus, 1), 2), 3) ...
            if cfg.DISPLAY_CHORDS and item.has_chords() and item.type == 'verse': #for verses with chords, we move the label down 
              new_y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.SONGLINE_SIZE, y_offset=y+cfg.SONGCHORD_SIZE+cfg.SONGCHORD_SPACE, x_offset=0, line_space=cfg.SONGLINE_SPACE, page_mapping=page_mapping, line=label)
            else:       
              new_y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.SONGLINE_SIZE, y_offset=y, x_offset=0,
                               line_space=cfg.SONGLINE_SPACE, page_mapping=page_mapping, line=label)
            if item.type not in VARIABLE_INDENT: # standard indent, with chunk body on next line
              y = new_y                          # so we update y ... in other cases y not updated, so same line used
            #else: ignore new_y and we print on same line below


          # shrink font size, or wrap the line if that lets us fit
          # if resize != 0 we are shrinking, else we wrap
          font_size = cfg.SONGLINE_SIZE
          if cfg.RESIZE_PERCENT == 0:
            # font size does not change.  
            font_size = font_size  
   
          else:
            # reduce font size as much as needed but don't pass x% original
            while (label_length + myStringWidth(line.text, cfg.FONT_FACE, font_size)) > (page_mapping.endx - page_mapping.startx) and font_size > cfg.SONGLINE_SIZE * cfg.RESIZE_PERCENT:
              font_size = font_size * 0.99 # reduce 1%
              #print 'reducing from', cfg.SONGLINE_SIZE, 'to', font_size, '%2.2f%%' % (font_size / cfg.SONGLINE_SIZE)
            
          # we have a font -- lets use it
          #DBG:sav_y = y
          if cfg.DISPLAY_CHORDS and item.has_chords():
            y = print_chords(pdf, cfg, font_size=font_size, y_offset=y, x_offset=label_length, page_mapping=page_mapping, line=line)
          y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=font_size, y_offset=y, x_offset=label_length,
                         line_space=cfg.SONGLINE_SPACE, page_mapping=page_mapping, line=line.text)
          #DBG:pdf.setStrokeColor('green')
          #DBG:pdf.rect(page_mapping.startx+label_length, page_mapping.starty-(sav_y),
          #DBG:    pdf.stringWidth(line.text, cfg.FONT_FACE, font_size), -line.height)
          #DBG:pdf.setStrokeColor('red')
          #DBG:pdf.rect(page_mapping.startx+label_length, page_mapping.starty-(sav_y),
          #DBG:    pdf.stringWidth(line.text, cfg.FONT_FACE, font_size), sav_y-y)
          #DBG:# reset
          #DBG:pdf.setStrokeColor('black')
          #DBG:pdf.setFillColor('black')

      if item.last_chunk:
        y += cfg.SONGCHUNK_B4
        for line in item.copyright_footer:
          y = print_line(pdf, font_face=cfg.FONT_FACE, font_size=cfg.COPYRIGHT_SIZE, y_offset=y,
                         line_space=0, page_mapping=page_mapping, line=line)
          y += cfg.COPYRIGHT_SPACE        # COPYRIGHT SPACE is padding between copyright lines 

      # any parting space
      y += item.height_after

        #DBG:pdf.rect(page_mapping.startx+5, page_mapping.starty - (starty+cfg.SONGLINE_SIZE), 20, starty-y)
    # INDEX
    elif isinstance(item, Index) and cfg.DISPLAY_INDEX != INDEX_OFF: # top-level index which contains index entries
      if cfg.DISPLAY_INDEX == INDEX_NO_PAGE_BREAK:
        y += cfg.INDEX_TITLE_B4  # only add space when index not starting on a new page
      y = print_line(pdf, font_face=cfg.INDEX_TITLE_FONT, font_size=cfg.INDEX_TITLE_SIZE, y_offset=y, 
                      line_space=cfg.INDEX_TITLE_SPACE, page_mapping=page_mapping, line="Alphabetical Index")

    # SCRIP INDEX
    elif isinstance(item, ScripIndex) and cfg.DISPLAY_SCRIP_INDEX != INDEX_OFF: # top-level scrip_index which contains index entries
      if cfg.DISPLAY_SCRIP_INDEX == INDEX_NO_PAGE_BREAK:
        y += cfg.INDEX_TITLE_B4  # only add space when scrip index not starting on a new page
      y = print_line(pdf, font_face=cfg.INDEX_TITLE_FONT, font_size=cfg.INDEX_TITLE_SIZE, y_offset=y, 
                      line_space=cfg.INDEX_TITLE_SPACE, page_mapping=page_mapping, line="Scripture Index")

    # CAT INDEX
    elif isinstance(item, CatIndex) and cfg.DISPLAY_CAT_INDEX != INDEX_OFF: # top-level cat_index which contains index entries
      if cfg.DISPLAY_CAT_INDEX == INDEX_NO_PAGE_BREAK:
        y += cfg.INDEX_TITLE_B4  # adding space because cat_index not starting on a new page
      y = print_line(pdf, font_face=cfg.INDEX_TITLE_FONT, font_size=cfg.INDEX_TITLE_SIZE, y_offset=y, 
                      line_space=cfg.INDEX_TITLE_SPACE, page_mapping=page_mapping, line="Category Index")

    # CAT INDEX Category
    elif isinstance(item, Category) and cfg.DISPLAY_CAT_INDEX != INDEX_OFF: # Category inside cat_index
      y += cfg.INDEX_CAT_B4  # add space before the category
      y = print_line(pdf, font_face=cfg.INDEX_CAT_FONT, font_size=cfg.INDEX_CAT_SIZE, y_offset=y, 
                      line_space=cfg.INDEX_CAT_SPACE, page_mapping=page_mapping, line=item.category)

    # CAT INDEX ITEM
    elif isinstance(item, CatIndexEntry) and cfg.DISPLAY_CAT_INDEX != INDEX_OFF:
      # print only the song number at this time -- don't save y since we are going to print on the line again
      print_line(pdf, font_face=cfg.INDEX_SONG_FONT, font_size=cfg.INDEX_SONG_SIZE, y_offset=y, line_space=cfg.INDEX_SONG_SPACE,
          page_mapping=page_mapping, line=str(item.song.num))
      # now print the index text with a consistent x offset so everything lines up
      y = print_line(pdf, font_face=cfg.INDEX_SONG_FONT, font_size=cfg.INDEX_SONG_SIZE, y_offset=y, line_space=cfg.INDEX_SONG_SPACE,
          x_offset=max(cfg.INDEX_SONG_SIZE, cfg.INDEX_FIRST_LINE_SIZE)*2, page_mapping=page_mapping, line=item.index_text)

    # INDEX ITEMS (after CatIndexEntry because CatIndexEntry is a subclass of IndexEntry)
    elif isinstance(item, IndexEntry) and (cfg.DISPLAY_INDEX != INDEX_OFF or cfg.DISPLAY_SCRIP_INDEX != INDEX_OFF):
      if item.is_song_title:
        LINE_SIZE = cfg.INDEX_SONG_SIZE
        LINE_SPACE= cfg.INDEX_SONG_SPACE
        FONT      = cfg.INDEX_SONG_FONT
      else:
        LINE_SIZE = cfg.INDEX_FIRST_LINE_SIZE
        LINE_SPACE= cfg.INDEX_FIRST_LINE_SPACE
        FONT      = cfg.INDEX_FIRST_LINE_FONT

      # print only the song number at this time -- don't save y since we are going to print on the line again
      print_line(pdf, font_face=FONT, font_size=LINE_SIZE, y_offset=y, line_space=LINE_SPACE,
          page_mapping=page_mapping, line=str(item.song.num))
      # now print the index text with a consistent x offset so everything lines up
      y = print_line(pdf, font_face=FONT, font_size=LINE_SIZE, y_offset=y, line_space=LINE_SPACE,
          x_offset=max(cfg.INDEX_SONG_SIZE, cfg.INDEX_FIRST_LINE_SIZE)*2, page_mapping=page_mapping, line=item.index_text)
  
  # restore original clip settings
  pdf.restoreState()

  # debug -- print page (small page here) rect
  #DBG:print '%d x %d rect at (%d, %d)' % (page_mapping.endx-page_mapping.startx, page_mapping.endy-page_mapping.starty,
  #DBG:    page_mapping.startx, page_mapping.starty)
  #XXX: uncomment last 2 lines to have a border around each page
  #pdf.rect(page_mapping.startx, page_mapping.starty,
  #    page_mapping.endx-page_mapping.startx,page_mapping.endy-page_mapping.starty,
  #    fill=0)
  if page_height(page_mapping.page) != y:
    print 'Page:', pdf.getPageNumber(), 'Expected page height:', page_height(page_mapping.page), 'not equal to actual page height:', y
    #DBG:pdf.rect(page_mapping.startx, page_mapping.starty,
    #DBG:    page_mapping.endx-page_mapping.startx,-page_height(page_mapping.page),
    #DBG:    fill=0)


def format(songbook, pdf, cfg):
  if isinstance(songbook, basestring):
    songbook = parse(songbook, cfg)    # parse the XML into objects

  # calculate the space needed for the songbook pieces
  calc_heights(songbook, cfg)

  # returns a list of pages: each page is a list of things to show on that page 
  # Songbook and Song objects only count for titles and headers chunks have to be listed separate
  pages = paginate(songbook, cfg)

  pages_ordered = cfg.page_layout.page_order(pages)

  # pdf object creation must be after the page layout methods are run because the page layout can change the paper size
  pdf = canvas.Canvas(pdf, pagesize=(cfg.PAPER_WIDTH, cfg.PAPER_HEIGHT))

  # set the PDF title
  pdf.setTitle(songbook.title)

  for physical_page in pages_ordered:
    for page_mapping in physical_page:
      format_page(pdf, cfg, page_mapping)

    # debug -- print page (small page here) rect
    #pdf.rect(cfg.PAPER_MARGIN_LEFT, cfg.PAPER_HEIGHT-cfg.PAPER_MARGIN_TOP,
        #cfg.PAPER_WIDTH-cfg.PAPER_MARGIN_RIGHT-cfg.PAPER_MARGIN_LEFT,(cfg.PAPER_MARGIN_BOTTOM+cfg.PAPER_MARGIN_TOP)-cfg.PAPER_HEIGHT,
        #fill=0)
    # done with (sub/virtual) pages that are written on one physical page -- on to next page
    pdf.showPage()


  # now save
  pdf.save()


def read_config_file(filename):
  return read_config(open(filename).read())


def read_config(config_string):
  config = OptionParser()
  config.add_option('--songs-to-print',             type="string",          dest="SONGS_TO_PRINT")
  config.add_option('--paper-size',                 type="string",          dest="PAPER_SIZE")
  config.add_option('--paper-orientation',          type="string",          dest="PAPER_ORIENTATION")
  config.add_option('--paper-margin-left',          type="float",           dest="PAPER_MARGIN_LEFT")
  config.add_option('--paper-margin-right',         type="float",           dest="PAPER_MARGIN_RIGHT")
  config.add_option('--paper-margin-top',           type="float",           dest="PAPER_MARGIN_TOP")
  config.add_option('--paper-margin-bottom',        type="float",           dest="PAPER_MARGIN_BOTTOM")

  config.add_option('--page-layout',                type="string",          dest="PAGE_LAYOUT_NAME")
  config.add_option('--page-margin-left',           type="float",           dest="PAGE_MARGIN_LEFT")
  config.add_option('--page-margin-right',          type="float",           dest="PAGE_MARGIN_RIGHT")
  config.add_option('--page-margin-top',            type="float",           dest="PAGE_MARGIN_TOP")
  config.add_option('--page-margin-bottom',         type="float",           dest="PAGE_MARGIN_BOTTOM")

  config.add_option('--binder-margin',              type="float",           dest="BINDER_MARGIN")

  config.add_option('--font-face',                  type="string",          dest="FONT_FACE")

  config.add_option('--ccli',                       type="string",          dest="CCLI")

  config.add_option('--columns',                    type="int",             dest="COLUMNS")

  config.add_option('--booktitle-size',             type="int",             dest="BOOKTITLE_SIZE")
  config.add_option('--booktitle-space',            type="int",             dest="BOOKTITLE_SPACE")
  config.add_option('--hide-booktitle',             type="string",          dest="HIDE_BOOKTITLE")

  config.add_option('--start-song-on-new-page',     type="string",          dest="START_SONG_ON_NEW_PAGE")
  config.add_option('--songtitle-format',           type="string",          dest="SONGTITLE_FORMAT")
  config.add_option('--songtitle-size',             type="int",             dest="SONGTITLE_SIZE")
  config.add_option('--songtitle-space',            type="int",             dest="SONGTITLE_SPACE")
  config.add_option('--song-space-after',           type="int",             dest="SONG_SPACE_AFTER")
  config.add_option('--songchunk-b4',               type="int",             dest="SONGCHUNK_B4")
  config.add_option('--songline-size',              type="int",             dest="SONGLINE_SIZE")
  config.add_option('--songline-space',             type="int",             dest="SONGLINE_SPACE")
  config.add_option('--songchord-size',             type="int",             dest="SONGCHORD_SIZE")
  config.add_option('--songchord-space',            type="int",             dest="SONGCHORD_SPACE")
  config.add_option('--display-chords',             type="string",          dest="DISPLAY_CHORDS")

  config.add_option('--small-size',                 type="int",             dest="SMALL_SIZE")
  config.add_option('--small-space',                type="int",             dest="SMALL_SPACE")

  config.add_option('--scripture-location',         type="string",          dest="SCRIPTURE_LOCATION")

  config.add_option('--copyright-size',             type="int",             dest="COPYRIGHT_SIZE")
  config.add_option('--copyright-space-b4',         type="int",             dest="COPYRIGHT_SPACE")

  config.add_option('--resize-percent',             type="int",             dest="RESIZE_PERCENT")

  config.add_option('--display-cat-index',          type="string",          dest="DISPLAY_CAT_INDEX")
  config.add_option('--display-scrip-index',        type="string",          dest="DISPLAY_SCRIP_INDEX")
  config.add_option('--display-index',              type="string",          dest="DISPLAY_INDEX")
  config.add_option('--include-first-line',         type="string",          dest="INCLUDE_FIRST_LINE")
  config.add_option('--index-title-font',           type="string",          dest="INDEX_TITLE_FONT")
  config.add_option('--index-title-b4',             type="int",             dest="INDEX_TITLE_B4")
  config.add_option('--index-title-size',           type="int",             dest="INDEX_TITLE_SIZE")
  config.add_option('--index-title-space',          type="int",             dest="INDEX_TITLE_SPACE")
  config.add_option('--index-cat-font',             type="string",          dest="INDEX_CAT_FONT")
  config.add_option('--index-cat-b4',               type="int",             dest="INDEX_CAT_B4")
  config.add_option('--index-cat-size',             type="int",             dest="INDEX_CAT_SIZE")
  config.add_option('--index-cat-space',            type="int",             dest="INDEX_CAT_SPACE")
  config.add_option('--index-cat-exclude',          type="string",          dest="INDEX_CAT_EXCLUDE")
  config.add_option('--index-song-font',            type="string",          dest="INDEX_SONG_FONT")
  config.add_option('--index-song-size',            type="int",             dest="INDEX_SONG_SIZE")
  config.add_option('--index-song-space',           type="int",             dest="INDEX_SONG_SPACE")
  config.add_option('--index-first-line-font',      type="string",          dest="INDEX_FIRST_LINE_FONT")
  config.add_option('--index-first-line-size',      type="int",             dest="INDEX_FIRST_LINE_SIZE")
  config.add_option('--index-first-line-space',     type="int",             dest="INDEX_FIRST_LINE_SPACE")

  config.add_option('--debug-margins',              type="string",          dest="DEBUG_MARGINS")

  (options, args) = config.parse_args(config_string.split())

  if options.PAPER_ORIENTATION == 'portrait':
    options.PAPER_WIDTH, options.PAPER_HEIGHT = getattr(reportlab.lib.pagesizes, options.PAPER_SIZE)
  else:
    options.PAPER_HEIGHT, options.PAPER_WIDTH = getattr(reportlab.lib.pagesizes, options.PAPER_SIZE)

  if options.SONGTITLE_FORMAT:
    if options.SONGTITLE_FORMAT == 'None':  # special case for when the option field is left blank in HTML
      options.SONGTITLE_FORMAT = string.Template('$title')
    else:
      options.SONGTITLE_FORMAT = string.Template(options.SONGTITLE_FORMAT.replace(r'\s', ' ') + ' $title')
  else:
    options.SONGTITLE_FORMAT = string.Template(r'$num. $title')

  if options.HIDE_BOOKTITLE and options.HIDE_BOOKTITLE.lower() == 'yes':
    options.HIDE_BOOKTITLE = True
  else:
    options.HIDE_BOOKTITLE = False

  if options.START_SONG_ON_NEW_PAGE and options.START_SONG_ON_NEW_PAGE.lower() == 'yes':
    options.START_SONG_ON_NEW_PAGE = True
  else:
    options.START_SONG_ON_NEW_PAGE = False

  if options.DISPLAY_CHORDS and options.DISPLAY_CHORDS.lower() == 'yes':
    options.DISPLAY_CHORDS = True
  else:
    options.DISPLAY_CHORDS = False

  if options.DEBUG_MARGINS and options.DEBUG_MARGINS.lower() == 'yes':
    options.DEBUG_MARGINS = True
  else:
    options.DEBUG_MARGINS = False

  if options.DISPLAY_INDEX and options.DISPLAY_INDEX.lower() == INDEX_ON_NEW_PAGE.lower():
    options.DISPLAY_INDEX = INDEX_ON_NEW_PAGE
  elif options.DISPLAY_INDEX and options.DISPLAY_INDEX.lower() == INDEX_NO_PAGE_BREAK.lower():
    options.DISPLAY_INDEX = INDEX_NO_PAGE_BREAK
  else:
    options.DISPLAY_INDEX = INDEX_OFF

  if options.DISPLAY_SCRIP_INDEX and options.DISPLAY_SCRIP_INDEX.lower() == INDEX_ON_NEW_PAGE.lower():
    options.DISPLAY_SCRIP_INDEX = INDEX_ON_NEW_PAGE
  elif options.DISPLAY_SCRIP_INDEX and options.DISPLAY_SCRIP_INDEX.lower() == INDEX_NO_PAGE_BREAK.lower():
    options.DISPLAY_SCRIP_INDEX = INDEX_NO_PAGE_BREAK
  else:
    options.DISPLAY_SCRIP_INDEX = INDEX_OFF

  if options.DISPLAY_CAT_INDEX and options.DISPLAY_CAT_INDEX.lower() == INDEX_ON_NEW_PAGE.lower():
    options.DISPLAY_CAT_INDEX = INDEX_ON_NEW_PAGE
  elif options.DISPLAY_CAT_INDEX and options.DISPLAY_CAT_INDEX.lower() == INDEX_NO_PAGE_BREAK.lower():
    options.DISPLAY_CAT_INDEX = INDEX_NO_PAGE_BREAK
  else:
    options.DISPLAY_CAT_INDEX = INDEX_OFF

  if not options.RESIZE_PERCENT and options.RESIZE_PERCENT != 0:
    options.RESIZE_PERCENT = 1
  else:
    options.RESIZE_PERCENT = options.RESIZE_PERCENT / 100.0

  if not options.INDEX_CAT_EXCLUDE:
    options.INDEX_CAT_EXCLUDE = []
  else:
    options.INDEX_CAT_EXCLUDE = [c.strip() for c in options.INDEX_CAT_EXCLUDE.split(',')]

  # Margin Conversion from inches to pt
  options.PAPER_MARGIN_LEFT = options.PAPER_MARGIN_LEFT * inch
  options.PAPER_MARGIN_RIGHT = options.PAPER_MARGIN_RIGHT * inch
  options.PAPER_MARGIN_TOP = options.PAPER_MARGIN_TOP * inch
  options.PAPER_MARGIN_BOTTOM = options.PAPER_MARGIN_BOTTOM * inch

  options.PAGE_MARGIN_LEFT = options.PAGE_MARGIN_LEFT * inch
  options.PAGE_MARGIN_RIGHT = options.PAGE_MARGIN_RIGHT * inch
  options.PAGE_MARGIN_TOP = options.PAGE_MARGIN_TOP * inch
  options.PAGE_MARGIN_BOTTOM = options.PAGE_MARGIN_BOTTOM * inch

  options.BINDER_MARGIN = options.BINDER_MARGIN * inch


  # page layout init after almost everything so it can play with options as needed
  options.page_layout     = page_layouts[options.PAGE_LAYOUT_NAME](options)  

  # these go last since they are derived from the layout
  options.PAGE_WIDTH      = options.page_layout.get_page_width()
  options.PAGE_HEIGHT     = options.page_layout.get_page_height()

  if not options.CCLI or options.CCLI == 'None':
    options.CCLI          = '__________'

  return options

def available_fonts():
  import reportlab.pdfbase.pdfmetrics as pdfmetrics
  # list(set(...)) to make list unique
  return sorted(list(set(list(pdfmetrics.standardFonts) + pdfmetrics.getRegisteredFontNames())))

def get_options(config_option):
  if config_option == '--paper-size':
    return [s for s in dir(reportlab.lib.pagesizes) if isinstance(getattr(reportlab.lib.pagesizes, s), tuple) ]

  elif config_option in ('--font-face', '--index-title-font', '--index-cat-font', '--index-song-font', '--index-first-line-font'):
    return available_fonts()

  elif config_option == '--page-layout':
    return get_page_layouts()

  elif config_option == '--paper-orientation':
    return ['portrait', 'landscape']

  elif config_option in ('--display-chords', '--hide-booktitle', '--start-song-on-new-page'):
    return ['no', 'yes']

  elif config_option == '--display-index':
    return [INDEX_ON_NEW_PAGE, INDEX_NO_PAGE_BREAK, INDEX_OFF]
  #  return [INDEX_ON_NEW_PAGE, INDEX_AFTER_LAST_SONG, INDEX_OFF]

 # elif config_option == '--display-cat-index':
 #   return [INDEX_ON_NEW_PAGE, CAT_INDEX_AFTER_INDEX, INDEX_OFF]

  elif config_option == '--scripture-location':
    return [SCRIPTURE_IN_TITLE, SCRIPTURE_UNDER_TITLE]

def format2pdf(songbook_file, pdf_out_file, config_string):
  return format(songbook_file, pdf_out_file, read_config(config_string))


if __name__ == '__main__':
  import sys
  format(sys.argv[1], sys.argv[2], read_config_file(sys.argv[3]))



  



  



