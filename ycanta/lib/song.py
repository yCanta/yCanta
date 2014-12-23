try: # try c version for speed then fall back to python
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import ycanta.model

def load(path):
  """Given filename or file object, parse xml and load to song object"""
  def get_piece(dom, piece, nullable=True):
    if dom.find(piece) != None and dom.find(piece).text != None :
      return unicode(dom.find(piece).text)
    else:
      if nullable == True:
        return None
      else:
        return u'Unknown'

  def to_boolean(s):
    if(s is None
        or len(s.strip()) == 0
        or s.strip().lower().startswith('no')
        or s.strip().lower().startswith('false')
        or s.strip().lower().startswith('off')):
      return False
    else:
      return True


  dom = ET.parse(path)

  content = ET.Element('song')
  content.extend(dom.findall('chunk'))


  song = ycanta.model.Song(
      title        = get_piece(dom, 'stitle', nullable=False),
      author       = get_piece(dom, 'author', nullable=False),
      scripture    = get_piece(dom, 'scripture_ref'),
      introduction = get_piece(dom, 'introduction'),
      key          = get_piece(dom, 'key'),
      categories   = get_piece(dom, 'categories'),
      ccli         = to_boolean(get_piece(dom, 'cclis')),
      copyright    = get_piece(dom, 'copyright'),
      content      = ET.tostring(content, encoding='utf-8').decode('utf-8'),
      )

  return song

def song_to_str(song):
  return ET.tostring(song_to_ET(song))

def song_to_ET(song):
  dom = ET.Element('song')
  dom.attrib['format-version'] = '0.1'
  ET.SubElement(dom, 'stitle').text        = song.title
  ET.SubElement(dom, 'author').text        = song.author
  ET.SubElement(dom, 'scripture_ref').text = song.scripture
  ET.SubElement(dom, 'introduction').text  = song.introduction
  ET.SubElement(dom, 'key').text           = song.key
  ET.SubElement(dom, 'categories').text    = song.categories
  ET.SubElement(dom, 'cclis').text         = song.ccli
  chunks = ET.XML(song.content)
  dom.extend(chunks.findall('chunk'))
  ET.SubElement(dom, 'copyright').text     = song.copyright

  return dom



