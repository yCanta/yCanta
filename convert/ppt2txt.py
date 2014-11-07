#!/usr/bin/env python
import os
import re
import sys
import time
import signal
import os.path
import subprocess

chunk_delimiter = re.compile(r'\s*\n\s*\n', re.M|re.S) # whitespace*,newline,whitespace*,newline -- i.e. 1 complete blank line

def convert(input):

  (stdout,stderr) = subprocess.Popen(['catppt', input], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
  stdout = stdout.replace('\x0b', '\n') # replace vertical TAB (hex 0x0b) with new line

  if stderr.strip(): # we get error
    print stderr

  text_out_chunks = []
  chunk_type = []

  # loop through generated textN.html files
  possible_title = []  # we put this as the first chunk and use the filename instead
  ccli = ''
  for chunk in chunk_delimiter.split(stdout):

    if 'ccli' in chunk.lower():
      ccli = chunk.strip()

    if '\n' not in chunk:
      possible_title.append(chunk.strip())
      continue

    if 'chorus' in chunk.lower():
      #remove 'chorus' and associated text from chunk
      chorus_pat = re.compile('^[^\w]*chorus[^\w]*', re.I)
      chunk = re.sub(chorus_pat, '', chunk)
      if chunk not in text_out_chunks:
        chunk_type.append('chorus')
        text_out_chunks.append(chunk)

    else:
      if chunk not in text_out_chunks:
        chunk_type.append('verse')
        text_out_chunks.append(chunk)

  return dict(title = input.replace('\\', '/').split('/')[-1].replace('.ppt', '').replace('.PPT', '').replace('+', ' ').replace('-', ' ').replace('_', ' '),
      chunks = ['\n'.join(possible_title)]+text_out_chunks,
      chunk_type = ['no label']+chunk_type, cclis=ccli, categories=['Powerpoint Import'])

def main(input, output):

  result_dict = convert(input)

  f = open(output, 'w')
  f.write('Title: ' + result_dict['title'])
  f.write('\n')
  f.write('CCLI: ' + result_dict['cclis'])
  f.write('\n')
  i = 0
  while i < len(result_dict['chunks']) and i < len(result_dict['chunk_type']):
    f.write('\n')
    f.write(result_dict['chunk_type'][i])
    f.write('\n')
    f.write(result_dict['chunks'][i])
    f.write('\n')
    i += 1
  f.close()

if __name__ == '__main__':
  assert len(sys.argv) == 3
  main(sys.argv[1], sys.argv[2])
