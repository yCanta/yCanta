try: # try c version for speed then fall back to python
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import ycanta.model

CHORD_SPACE_RATIO = 0.45

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
  return ET.tostring(song_to_ET(song), encoding='utf-8').decode('utf-8')

def song_to_ET(song):
  dom = ET.Element('song')
  dom.attrib['format-version'] = '0.1'
  ET.SubElement(dom, 'stitle').text        = song.title
  ET.SubElement(dom, 'author').text        = song.author
  ET.SubElement(dom, 'scripture_ref').text = song.scripture
  ET.SubElement(dom, 'introduction').text  = song.introduction
  ET.SubElement(dom, 'key').text           = song.key
  ET.SubElement(dom, 'categories').text    = song.categories
  ET.SubElement(dom, 'cclis').text         = unicode(song.ccli)
  chunks = ET.XML(song.content.encode('utf-8'))
  dom.extend(chunks.findall('chunk'))
  ET.SubElement(dom, 'copyright').text     = song.copyright
  return dom

def song_chunks_to_mono(song, exclude_chords=False):
  chunks = []
  for chunk in song_to_ET(song).findall('chunk'):
    chunk_text =  chunk_to_mono(chunk, exclude_chords)
    chunks.append(chunk_text)

  return chunks
 
def chunk_to_mono(chunk, exclude_chords=False):
  def is_chord_line(line):
    return line.find('c') is not None

  def strip_chord(line):
    '''strip chords from a line (ET object), return string'''
    text = line.text or ''
    for c in line.findall('c'):
      text += c.tail or ''
    return text

  def expand_chord(line):
    '''expands chords that are in xml format into monospaced format'''

    #------------- taken from pdfformatter.parse_song       
    # parse chords from line 
    text = line.text or ''
    chords = {}                             # chords is a dictionary of (position, text)

    # parse chords and rest of line text
    for c in line.findall('c'):
      chords[len(text)] = c.text            # len(text) is offset in text where chord appears
      text += c.tail or ''
    #-------------

    str_chords = ''
    for offset in sorted(chords.keys()):
      str_chords += ' '*(offset-len(str_chords)) + chords[offset]

    # Add space to the end of the chord line to make the chord recognized as a chord when reimporting.
    w = str_chords.count(' ') + 0.0
    char = len(str_chords) - w

    w_ad = int(((CHORD_SPACE_RATIO * char)/(1-CHORD_SPACE_RATIO) - w) + 1)
    str_chords += ' '*w_ad

    expanded_line = str_chords + '\n' + text.rstrip()
    return expanded_line

  
  # Start of actual function ...
  chunk_text=[]
  lines = chunk.findall('line')
  for line in lines:
    if is_chord_line(line):
      if exclude_chords:
        chunk_text.append(strip_chord(line))
      else:
        chunk_text.append(expand_chord(line))
    else:
      chunk_text.append(line.text or "")

  return '\n'.join(chunk_text)




