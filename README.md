yCanta
======

is a web-based program designed to quickly create, manage, and present/export songbooks for church worship.  It is open source, written in Python, and uses Turbogears, Report Lab, Element Tree, and JQuery.  It has been developed and tested on linux.  Songs and songbooks are stored as xml.

Recent Changes
--------------
 - *2014-11-07* - Upgraded packages and created requirements.txt for easy pip install in virtualenv
 - *2013-06-25* - Added option to launch secondary presentation windows and ability to present chords.
 - *2012-11-29* - Added option to wrap lines and chords in a song.
 - *2012-11-16* - Presentation mode is now functional on chrome and opera.
 - *2012-11-14* - Songs can now be transposed while editing.
 - *2011-11-20* - Search on the site now includes all song content.
 - *2011-04-18* - Added ability to edit songs w/o leaving a songbook or song page.
 - *2011-04-06* - Added sections to songbooks, no support yet in export.
 - *2011-03-18* - Added information button to song_view currently only showing all songbooks that include the song.
 - *2011-03-17* - Re-factored indexes, they now include categorical, scriptural, and alphabetical in that order.  All indexes can be printed with or without page break or can be turned off.
 - *2011-01-xx* - Added more options to pdf export including category index.

Install
-------
git pull ...
cd yCanta
virtualenv .
. bin/activate
pip install -r requirements.txt
python start-webapp.py

Issues
------

PEAK Rules package doesn't have a verifiable pypi package available.  It can be installed like so:
  pip install --allow-external PEAK-Rules --allow-unverified PEAK-Rules TurboGears
