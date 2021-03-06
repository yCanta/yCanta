yCanta
======

is a web-based program designed to quickly create, manage, and present/export songbooks for church worship.  It is open source, written in Python, and uses Turbogears, Report Lab, Element Tree, and JQuery.  It has been developed and tested on linux.  Songs and songbooks are stored as xml.

Recent Changes
--------------
 - *2014-11-22* - Allowed export to use configurations from other songbooks 
 - *2014-11-21* - PDF formatter enhancements: fix overflow issue, and infinite loop with large margins
 - *2014-11-20* - Improvements to song search in app: ignore punctuation when searching, enable a:author search
 - *2014-11-17* - Songs and songbooks now have nice filenames
 - *2014-11-16* - New presentation mode key strokes: e for endings, 0 for 10th verse
 - *2014-11-14* - Presentation mode now supports webkit browsers (Chrome, Safari, etc)
 - *2014-11-12* - Presentation mode search now includes song titles
 - *2014-11-09* - Windows support and scan of songs and songbooks on first run, license as UNLICENSE
 - *2014-11-07* - Upgraded packages and created requirements.txt for easy pip install in virtualenv
 - *2013-06-25* - Added option to launch secondary presentation windows and ability to present chords.
 - *2012-11-29* - Added option to wrap lines and chords in a song.
 - *2012-11-16* - Presentation mode is now functional on chrome and opera.
 - *2012-11-14* - Songs can now be transposed while editing.
 - *2011-11-20* - Search on the site now includes all song content.
 - *2011-04-18* - Added ability to edit songs w/o leaving a songbook or song page.
 - *2011-04-06* - Added sections to songbooks, no support yet in export.
 - *2011-03-18* - Added information button to song view currently only showing all songbooks that include the song.
 - *2011-03-17* - Re-factored indexes, they now include categorical, scriptural, and alphabetical in that order.  All indexes can be printed with or without page break or can be turned off.
 - *2011-01-xx* - Added more options to pdf export including category index.

Install
-------

On Linux:

    git clone <repo URI here>
    cd yCanta
    virtualenv .
    source bin/activate
    pip install -r requirements.txt
    python start-webapp.py

On Windows:

    Download and install Portable Python 2.7: http://portablepython.com/wiki/Download/ (minimal install should be ok)
    git clone <repo URI here>
    path\to\PortablePython\Python-Portable.exe windows-build.py d:\path\to\PortablePython d:\where\you\want\the\build\to\go

Issues
------

PEAK Rules package doesn't have a verifiable pypi package available.  It can be installed like so:

    pip install --allow-external PEAK-Rules --allow-unverified PEAK-Rules TurboGears
