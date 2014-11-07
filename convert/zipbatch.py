import shutil
import convert
import zipfile
import os.path
import tempfile
import webapp.c_utilities

def batchconvert(fileobj, categories):

  # strip out empty categories
  categories = [cat for cat in categories if cat.strip()]
  
  zip = zipfile.ZipFile(fileobj, 'r')

  temp_dir = tempfile.mkdtemp()

  for fn in zip.namelist():
    ext = fn.split('.')[-1]

    if ext in convert.converter_for_fileext:
      zip.extract(fn, temp_dir)

      result = convert.converter_for_fileext[ext](os.path.join(temp_dir, fn))
      # song_save(title, author, introduction, copyrights, types, chunk_list, path, categories, cclis, submit, new)
      webapp.c_utilities.song_save(
          result.get('title', ''),
          result.get('author', ''),
          result.get('introduction', ''),
          result.get('copyright', ''),
          result['chunk_type'],
          result['chunks'],
          '',   # no path, new song
          list(set(result.get('categories', [])+categories)), # keep the list unique but add our categories
          result.get('cclis', ''),
          '',   # no submit ... not from webbrowser form submit
          True) # it is new
    #else:
      #Not found ... what to do?

  # done with loop ... clean up dir
  shutil.rmtree(temp_dir)

