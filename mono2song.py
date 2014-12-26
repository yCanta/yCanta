import mono2song as m
import xml.sax.saxutils
import re
import sys
import re


def convert2file(r_path, w_path):
  song = convert2string(r_path)
  write = open(w_path, "w")
  write.write(song)
  write.close()
  return

def convert2string(r_path):
  # replace is for an oddity with some song files we had from the ME computer
  r_song = open(r_path, "rU").read().replace('\n\x1a', '')
  return string2string(r_song)

def string2file(w_path, string):
  song = string2string(string)
  write = open(w_path, "w")
  write.write(song)
  write.close() 
  return

def string2string(string):
  is_chord = 0
  # conversion for song2momo
  if string.find('<') != -1:
    w_song = ''
    r_song = string.splitlines(0)
    index = 0
    while index < len(r_song) -1:
      is_chord = m.is_chord(r_song[index])
      tmp1 = r_song[index]
      tmp2 = r_song[index+1]
      if (m.is_chord(tmp1) == 1) and (m.is_chord(tmp2) == 0):
        c = r_song[index]
        index = index + 1
        l = r_song[index]
        index = index + 1
        l = m.combine(c, l)
        w_song = w_song + '<line>' + l + '</line>\n'
      elif (m.is_chord(tmp1) == 0) and (tmp1.strip() != ''):
        l = r_song[index]
        index = index + 1
        w_song = w_song + l + '\n'
      else:
        index = index + 1   #avoids infinite loop if conditions not met
    return w_song + '</song>'  #this is ugly, but it works
  # conversion for standard mono2song
  else:
    string = xml.sax.saxutils.escape(string) #encodes song test to be html safe & = &amp; etc
    r_song = m.split_song(string)
    w_song = '<?xml version="1.0" encoding="utf-8"?>\n' + '<song format-version="0.1">\n'

    for chunk in r_song:
      chunk = chunk.split('\n')
    
      chunk_type = m.identify_chunk(chunk)

      if chunk_type == 'title':
        for line in chunk:
          if (line.strip() != '') and (line.find('-') == -1):
            w_song = w_song + '<title>' + line.strip().title() + '</title>'
            break
          
      elif chunk_type == 'author':
        for line in chunk:
          if (line.lower().find('author:') != -1) and (line.strip() != ''):
            w_song = w_song + '\n<author>' + line.lower().replace('author:', '').strip().title() + '</author>'
            break
          
      elif chunk_type == 'introduction':
        for line in chunk:
          if (line.lower().find('intro') != -1) and (line.strip() != ''):
            w_song = w_song + '\n<chunk type="introduction">' + line.lower().replace('introduction:', '').strip().title() + '</chunk>'
          
      elif chunk_type == 'chorus':
        w_song = w_song + '\n<chunk type="chorus" repeat="every-page">\n'
        index = 0
        while index < len(chunk) -2:
          tmp1 = chunk[index]
          tmp2 = chunk[index+1]
          if (m.is_chord(tmp1) == 1) and (m.is_chord(tmp2) == 0):
            c = chunk[index]
            index = index + 1
            l = chunk[index]
            index = index + 1
            l = m.combine(c, l)
          elif (m.is_chord(tmp1) == 0) and (tmp1.strip() != ''):
            l = chunk[index]
            # verse number removal (matches whitespace then number then ), ., or :
            l = re.sub('^([ \t]*)[0-9][).:]', r'\1  ', l)
            index = index + 1
          else:
            index = index + 1   #avoids infinite loop if conditions not met
          l = l.replace('Chorus:', '').strip()
          w_song = w_song + '<line>' + l + '</line>\n'
        w_song = w_song + '</chunk>'
   
      elif chunk_type == 'verse':
        w_song = w_song + '\n<chunk type="verse">\n'
        index = 0
        while index < len(chunk) -2:
          tmp1 = chunk[index]
          tmp2 = chunk[index+1]
          if (m.is_chord(tmp1) == 1) and (m.is_chord(tmp2) == 0):
            c = chunk[index]
            index = index + 1
            l = chunk[index]
            index = index + 1
            l = m.combine(c, l)
          elif (m.is_chord(tmp1) == 0) and (tmp1.strip() != ''):
            l = chunk[index]
            l = re.sub('[0-9].', '  ', l)
            index = index + 1
          else:
            index = index + 1   #avoids infinite loop if conditions not met
          l = l.replace('Chorus:', '').strip()
          w_song = w_song + '<line>' + l + '</line>\n'
        w_song = w_song + '</chunk>'
    
      elif chunk_type == 'bridge':
        w_song = w_song + '\n<chunk type="bridge">\n'
        index = 0
        while index < len(chunk) -2:
          tmp1 = chunk[index]
          tmp2 = chunk[index+1]
          if (m.is_chord(tmp1) == 1) and (m.is_chord(tmp2) == 0):
            c = chunk[index]
            index = index + 1
            l = chunk[index]
            index = index + 1
            l = m.combine(c, l)
          elif (m.is_chord(tmp1) == 0) and (tmp1.strip() != ''):
            l = chunk[index]
            l = re.sub('[0-9].', '  ', l)
            index = index + 1
          else:
            index = index + 1   #avoids infinite loop if conditions not met
          l = l.replace('Bridge:', '').strip()
          w_song = w_song + '<line>' + l + '</line>\n'
        w_song = w_song + '</chunk>'
        w_song = w_song.replace('\n<line></line>', '') #removes empty lines
  
    w_song = w_song + '\n</song>'
    #print w_song  
    return w_song

#determines whether a line is a chord
def is_chord(line):
  fraction = 0.45

  line = line            # not stripping any whitespace so we can manually make a line a chord line by adding extra space
  count = line.count(' ') + 0.0 
   
  if len(line) == 0 or not any(c.isalpha() for c in line):
    return 0  
  elif len(line) <= 4:        #for lines with one or two chords
    return 1
  elif (count/len(line) > fraction):  #for deciding whether line is a chord
    return 1
  else:                     #for lines that are not chords
    return 0

#breaks a string into paragraphs returning a list
def split_song(song_str):
  split_song = song_str.split('\n') #breaks string into lines
  verses = []
  newverse = ''
                                          
  for line in split_song:   #puts lines back together as paragraphs
    newverse = newverse + line + "\n"
    if line.strip() == '':
      verses.append(newverse)
      newverse = ''
  verses.append(newverse)   #appends new chunk at end of song if no empty line
  return verses

#identifies chunk as verse, bridge, chorus, or introduction
def identify_chunk(chunk):
  total = ''
  is_chord = 0
  for line in chunk:
    total = total + line
    if line.find('-----') != -1:
      return 'title'
    elif line.lower().find('author') != -1:
      return 'author'
    elif (line.lower().find('intro') or line.lower().find('introduction')) != -1:
      return 'introduction'
    elif (line.lower().find('chorus') != -1) and (line.lower().find('(chorus)') == -1):
      return 'chorus'
    elif line.lower().find('bridge') != -1: #too broad methinks
      return 'bridge'
  if total == '':
    return 'empty'
  else:
    return 'verse'

#combines 2 lines of text (used for inlining chords)
def combine(chord, text):
  #make text at least as long a chord length
  chord = unicode(chord, 'utf-8')
  if len(text) < len(chord):
    text+=' '*(len(chord) - len(text))

  #convert chord to dictionary with [start, chord]
  chords = {}
  for c in re.finditer(r'[\S]+', chord):
    chords[c.start()] = chord[c.start():c.end()]

  #combine
  line = unicode(xml.sax.saxutils.escape(text), 'utf-8')

  for offset in sorted(chords.keys(), reverse=True):
    line = line[:offset] + '<c>' + chords[offset] + '</c>' + line[offset:]
  
  return line.encode('utf-8')


if __name__ == '__main__':
  if len(sys.argv) != 3:
    print 'This program requires two arguments'
    sys.exit(1)
  convert2file(sys.argv[1], sys.argv[2])
