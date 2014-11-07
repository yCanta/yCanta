#!/bin/bash

function displaysong {
  echo "Content-type: text/xml"
  echo

  sed 's|<song|<?xml-stylesheet title="2html" type="text/xsl" href="./2html.xsl"?>\n<song|g' /home/song/workingcopy/trunk/songs/$1
}

function displayindex {
  echo "Content-type: text/html"
  echo

  echo "<html><head><title>Song Index</title></head><body>"
  echo "<h1>Song Index</h1><ul>"
  for fn in $(ls /home/song/workingcopy/trunk/songs/* | cut -f7 -d/)
  do
    echo "<li><a href=\"display.cgi?$fn\">$fn</a></li>"
  done
  echo "</ul></li></html>"
}

if [[ -n "$1" ]]
then
  displaysong $1
else
  displayindex 
fi


