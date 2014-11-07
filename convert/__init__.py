import ppt2txt
import songselect2txt
import praisetown
import higherpraise
import zipbatch

converter_for_fileext = dict(
    usr=songselect2txt.convert,
    ppt=ppt2txt.convert,
    )

batch_converter_for_fileext = dict(
    zip=zipbatch.batchconvert,
    )

converter_for_url     = {'www.praisetown.com':praisetown.convert,
                         'www.higherpraise.com':higherpraise.convert}

'''
Dictionary must be of form:

  D
  {
  'title'           : String - Title
  'author'          : String - Author
  'chunk_type'      : List of strings - chunk types
  'chunks'          : List of strings - chunk contents
  'copyright'       : String - Copyright information
  'cclis'           : String - CCLI song number
  'categories'      : List of strings - categories
  }



'''
