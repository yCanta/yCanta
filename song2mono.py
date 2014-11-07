try: # try c version for speed then fall back to python
  import xml.etree.cElementTree as ET
except ImportError:
  import xml.etree.ElementTree as ET

CHORD_SPACE_RATIO = 0.45


# recieves paths for read and write
def file2file(r_path, w_path):
  song = file2string(r_path)
  write = open(w_path, "w")
  write.write(song)
  write.close()
  return

# recieves path returns string
def file2string(path):
  string = open(path, "rU").read()
  return string2string(string)
  
# main function
def string2string(string):
  tree = ET.fromstring(string)

  lines = tree.findall('line')

  for line in lines:
    is_chord = is_chord_line(ET.tostring(line))
    if is_chord == 1:
      line.text = expand_chord(ET.tostring(line))
  return ET.tostring(tree)

# expands chords that are in xml format into monospaced format
def expand_chord(line):
  line = ET.fromstring(line)

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



def is_chord_line(line):
  if line.find('<c>') != -1:
    return 1
  else:
    return 0
