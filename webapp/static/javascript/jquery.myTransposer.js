/*!
 * jQuery Chord Transposer plugin v1.0
 * http://codegavin.com/projects/transposer
 *
 * Copyright 2010, Jesse Gavin
 * Dual licensed under the MIT or GPL Version 2 licenses.
 * http://codegavin.com/license
 *
 * Date: Sat Jun 26 21:27:00 2010 -0600
 * Modified by: Carl Hempelk 11/12/12
 */
(function($) {

  $.fn.transpose = function(options) {
    var opts = $.extend({}, $.fn.transpose.defaults, options);
    
    var currentKey = null;
    
    var keys = [
      { name: 'Ab',  value: 0,   type: 'F' },
      { name: 'A',   value: 1,   type: 'N' },
      { name: 'A#',  value: 2,   type: 'S' },
      { name: 'Bb',  value: 2,   type: 'F' },
      { name: 'B',   value: 3,   type: 'N' },
      { name: 'C',   value: 4,   type: 'N' },
      { name: 'C#',  value: 5,   type: 'S' },
      { name: 'Db',  value: 5,   type: 'F' },
      { name: 'D',   value: 6,   type: 'N' },
      { name: 'D#',  value: 7,   type: 'S' },
      { name: 'Eb',  value: 7,   type: 'F' },
      { name: 'E',   value: 8,   type: 'N' },
      { name: 'F',   value: 9,   type: 'N' },
      { name: 'F#',  value: 10,  type: 'S' },
      { name: 'Gb',  value: 10,  type: 'F' },
      { name: 'G',   value: 11,  type: 'N' },
      { name: 'G#',  value: 0,   type: 'S' }
    ];
  
    var getKeyByName = function (name) {
        if (name.charAt(name.length-1) == "m") {
          name = name.substring(0, name.length-1);
        }
        for (var i = 0; i < keys.length; i++) {
            if (name == keys[i].name) {
                return keys[i];
            }
        }
    };

    var getChordRoot = function (input) {
        if (input.length > 1 && (input.charAt(1) == "b" || input.charAt(1) == "#"))
            return input.substr(0, 2);
        else
            return input.substr(0, 1);
    };

    var getNewKey = function (oldKey, delta, targetKey) {
        var keyValue = getKeyByName(oldKey).value + delta;

        if (keyValue > 11) {
            keyValue -= 12;
        } else if (keyValue < 0) {
            keyValue += 12;
        }
        
        var i=0;
        if (keyValue == 0 || keyValue == 2 || keyValue == 5 || keyValue == 7 || keyValue == 10) {
            // Return the Flat or Sharp Key
            switch(targetKey.name) {
              case "A":
              case "A#":
              case "B":
              case "C":
              case "C#":
              case "D":
              case "D#":
              case "E":
              case "F#":
              case "G":
              case "G#":
                  for (;i<keys.length;i++) {
                    if (keys[i].value == keyValue && keys[i].type == "S") {
                      return keys[i];
                    }
                  }
              default:
                  for (;i<keys.length;i++) {
                    if (keys[i].value == keyValue && keys[i].type == "F") {
                      return keys[i];
                    }
                  }
            }
        }
        else {
            // Return the Natural Key
            for (;i<keys.length;i++) {
              if (keys[i].value == keyValue) {
                return keys[i];
              }
            }
        }
    };

    var getChordType = function (key) {
        switch (key.charAt(key.length - 1)) {
            case "b":
                return "F";
            case "#":
                return "S";
            default:
              return "N";
        }
    };

    var getDelta = function (oldIndex, newIndex) {
        if (oldIndex > newIndex)
            return 0 - (oldIndex - newIndex);
        else if (oldIndex < newIndex)
            return 0 + (newIndex - oldIndex);
        else
            return 0;
    };

    var transposeSong = function (target, key) {
      var newKey = getKeyByName(key);
      currentKey = getKeyByName($('input[name="key"]').val()) || newKey;

      if (currentKey.name == newKey.name) {
        return;
      }

      var delta = getDelta(currentKey.value, newKey.value);
     /*This is where we need to change the target for change.  Will also need to come up with way to fix spacing . . .    */
    
      $('#songsOl textarea').each(function() {
        var output = [];
        var lines = $(this).val().split("\n");
        var line = "";
        
        for (var i = 0; i < lines.length; i++) {
          line = lines[i];

          if (isChordLine(line))
            output.push(transposeLine(line, delta, newKey)); // need to change this from a wrapping operation to a tranpose
          else
            output.push(line);
        };

      $(this).val(output.join("\n"));
        
      });
        
      currentKey = newKey;
    };
    var transposeLine = function (line, delta, targetKey) {
       var newline = []
       var diff = 0
       var line = line.split(" ")
       for (var i = 0; i < line.length; i++) {
         if (line[i] != "") {
           var oldChordRoot = getChordRoot(line[i]);
           var newChordRoot = getNewKey(oldChordRoot, delta, targetKey);
           var newChord = newChordRoot.name + line[i].substr(oldChordRoot.length);
           newline.push(newChord);
           diff = line[i].length - newChord.length
         }
         else {
           if (diff < 0){
             diff = diff + 1
           }
           else {
             newline.push(line[i])
           }
         }
         for (; diff > 0; diff = diff -1) {
           newline.push("");
         }
       }
       return newline.join(" ")
    };

    var transposeChord = function (selector, delta, targetKey) {
        var el = $(selector);
        var oldChord = el.text();
        var oldChordRoot = getChordRoot(oldChord);
        var newChordRoot = getNewKey(oldChordRoot, delta, targetKey);
        var newChord = newChordRoot.name + oldChord.substr(oldChordRoot.length);
        el.text(newChord);

        var sib = el[0].nextSibling;
        if (sib && sib.nodeType == 3 && sib.nodeValue.length > 0 && sib.nodeValue.charAt(0) != "/") {
            var wsLength = getNewWhiteSpaceLength(oldChord.length, newChord.length, sib.nodeValue.length);
            sib.nodeValue = makeString(" ", wsLength);
        }
    };

    var getNewWhiteSpaceLength = function (a, b, c) {
        if (a > b)
            return (c + (a - b));
        else if (a < b)
            return (c - (b - a));
        else
            return c;
    };

    var makeString = function (s, repeat) {
        var o = [];
        for (var i = 0; i < repeat; i++) o.push(s);
        return o.join("");
    }
    
    
    var isChordLine = function (input) {
        var tokens = input.replace(/\s+/, " ").split(" ");

        // Try to find tokens that aren't chords
        // if we find one we know that this line is not a 'chord' line.
        for (var i = 0; i < tokens.length; i++) {
            if (!$.trim(tokens[i]).length == 0 && !tokens[i].match(opts.chordRegex))
                return false;
        }
        return true;
    };
    
    var wrapChords = function (input) {
        return input.replace(opts.chordReplaceRegex, "<span class='c'>$1</span>");
    };
    
    
    return $(this).each(function() {
    
      var startKey = $('input[name="key"]').val();
      if (!startKey || $.trim(startKey) == "") {
        startKey = "" 
      }

      
      currentKey = getKeyByName(startKey) || "";

      // Build tranpose links ===========================================
      var keyLinks = [];
      $(keys).each(function(i, key) {
          if (currentKey.name == key.name)
              keyLinks.push("<a href='#' id='"+key.name.replace('#','_')+"' class='selected'>" + key.name + "</a>");
          else
              keyLinks.push("<a href='#' id='"+key.name.replace('#','_')+"'>" + key.name + "</a>");
      });


      var $this = $(this);
      var keysHtml = $("<div class='transpose-keys'></div>");
      keysHtml.html(keyLinks.join(""));
      $("a", keysHtml).click(function(e) {
          e.preventDefault();
          transposeSong($this, $(this).text());
          $(".transpose-keys a").removeClass("selected");
          $(this).addClass("selected");
          $('input[name="key"]').val($(this).text())
          return false;
      });
      
      $(this).before(keysHtml);
    });
  };


  $.fn.transpose.defaults = {
    chordRegex: /^[A-G][b\#]?(2|5|6|7|9|11|13|6\/9|7\-5|7\-9|7\#5|7\#9|7\+5|7\+9|7b5|7b9|7sus2|7sus4|add2|add4|add9|aug|dim|dim7|m\/maj7|m6|m7|m7b5|m9|m11|m13|maj7|maj9|maj11|maj13|mb5|m|sus|sus2|sus4)*(\/[A-G][b\#]*)*$/,
    chordReplaceRegex: /([A-G][b\#]?(2|5|6|7|9|11|13|6\/9|7\-5|7\-9|7\#5|7\#9|7\+5|7\+9|7b5|7b9|7sus2|7sus4|add2|add4|add9|aug|dim|dim7|m\/maj7|m6|m7|m7b5|m9|m11|m13|maj7|maj9|maj11|maj13|mb5|m|sus|sus2|sus4)*)/g
  };

})(jQuery);
