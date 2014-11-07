#!/usr/bin/env python
import mono2song as m
import glob

file_names = glob.glob("/mnt/media/ME_Computer/Songscopy/*")
for file in file_names:
  path = file.replace('/mnt/media/ME_Computer/Songscopy', 'Songs/').lower()
  print path
  m.convert2file(file, path)
