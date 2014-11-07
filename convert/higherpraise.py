import urllib2
import re

def convert(input_url):
  '''return a dictionary as documented in __init__.py '''

  # Example higherpraise.com content
  # <div aligni="center"><!-- #BeginEditable "1" -->
  #   <table attrs=". . . ">
  #     ...
  #     <h1 align="center"><b><font class="default"><u>
  #       Title text </u></font><b></h1>
  #     <h4 align="center"><b><font class="default"><u>
  #       Author </u></font><b></h1>
  #     ...
  #     <pre><strong>Text, more text<br>More text<br><br>Next chunk
  #     </strong></pre>
  #     OR
  #     <pre><strong>Text, more text
  #     More text
  #
  #     Next Chunk
  #     </strong></pre>
  #     ...
  #   </table>
  # <!-- #EndEditable -->
  content = urllib2.urlopen(input_url).read()


  tag = re.compile(r'\<.*?\>')
  try:
    song_title = tag.sub('', re.split('\\<.*?h1.*?\\>', content)[1]).strip()
  except:
    song_title = ''
  try:
    song_author = tag.sub('', re.split('\\<.*?h4.*?\\>', content)[1]).strip()
  except:
    song_author = ''

  # now the real work -- parsing content into a song
  try:
    song_div = content.split('<pre>')[1].split('</pre>')[0].replace('&nbsp;', ' ')
  except:
    song_div = content.split('<PRE>')[1].split('</PRE>')[0].replace('&nbsp;', ' ')

  song_div = tag.sub('', song_div.replace('<br>','\n').replace('<BR>',''))


  chunks = []
  chunk_types = []
  lines = []

# Split into multiple chunks
  chunk_list = re.split('\n[ \t\r\f\v]*?\n(?=\s*?\S)', song_div)
  for chunk in chunk_list:
    if chunk.strip() in (song_title or song_author):
      continue
    chunks.append(chunk)
    chunk_types.append('verse')

# Leave as one chunk
#  chunks.append(song_div)
#  chunk_types.append('verse')

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

 
