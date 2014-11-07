import urllib2
import re

def convert(input_url):
  '''return a dictionary as documented in __init__.py '''

  # Example praisetown.com content
  # ...
  # <span class="ListHeader">Song:
  #  Song name </span>
  # ...
  # <ul class="ListHor">
  #  <li>Artist: Artist name</li>
  # </ul>
  # ...
  # <div id="Song">
  # Verse 1:<BR><BR>Verse starts<span class="Chord">D</span><span style="...">verse text continues</span><span class="Ch...
  # ...
  # </div id="Song">
  content = urllib2.urlopen(input_url).read()

  song_title = content.split('<span class="ListHeader">')[1].split('</span>')[0].replace('Song:', '').strip()
  song_author =content.split('<ul class="ListHor">')[1].split('</ul>')[0].replace('<li>', ' ').replace('</li>', ' ').replace('Artist:', '').strip()

  # now the real work -- parsing content into a song
  song_div =   content.split('<div id="Song">')[1].split('</div id="Song">')[0].replace('&nbsp;', ' ')

  chunks = []
  chunk_types = []
  lines = []
  for line in song_div.split('<BR>'):
    if not line.strip():  # if empty
      continue

    line = line.replace('\n', '').replace('\r', '')  # ignore embedded newlines -- this is HTML we are parsing -- only line breaks are <BR>

    # if this is a chorus, verse, or bridge intro line
    if ('chorus' in line.lower() or 'verse' in line.lower() or 'bridge' in line.lower()) and len(line.strip()) < 20:
      # append the previous bunch of lines into a chunk
      if(lines): # avoid adding an empty chunk
        chunks.append('\n'.join(lines))
        chunk_types.append(re.sub(r'(?i).*(chorus|verse|bridge).*', r'\1', line).lower()) # chunk type
        lines = []

    # got a non-empty line
    chords = {}
    result = ''
    start_of_line = True
    for part in line.split('<span'):
      if 'class="Chord"' in part:  # got a chord
        # part is: ' class="Chord">D</span>'
        c = part.split('>')[1].split('<')[0]
        chords[len(result)] = c # store the chord
      else: # not a chord
        # part is: 'Verse starts'
        #      or: ' style="...">verse text continues</span>'
        if '<' in part:
          part = part.split('<')[0]
        if '>' in part:
          part = part.split('>')[1]

        # add part text to line result
        result += part.lstrip() 

    # Now we've parsed all the parts in the line
    if chords:
      # add a chord line
      chord_line = ''
      for i in sorted(chords.keys()):
        len_dif = i - len(chord_line)
        chord_line += ' '*len_dif + chords[i]
      lines.append(chord_line)
    # add the line text
    lines.append(result)

  return dict(title=song_title, author=song_author, chunks=chunks, chunk_type=chunk_types)

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

 
