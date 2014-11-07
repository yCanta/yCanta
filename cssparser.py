# this is a truly simplistic pseudo-CSS parser to allow us to theme our PDF
# output
import re
import os.path

# regular expressions we are going to use
# =======================================

# uses non-greedy .*? to match inside of comment
comment_re = re.compile(r'/\*.*?\*/', re.M|re.S|re.X)

# first group is selector, second contains style rules for selected elements
chunk_re = re.compile(r'([^{}]*){(.*?)}', re.M|re.S|re.X)

# first and second groups are included in split - the 3rd group is junk
# Selectors can have alphanumeric, '@', '.', ':', '=', ']', '['
sel_split_re = \
    re.compile(r'([>,+]+)|([@a-zA-Z0-9.:=\[\]]+)|\s+', re.X|re.S|re.M)

# split a chunk of rules into individual rules -- group 1 is style type and
# group2 is style definition.  Breaks rule on semi-colon if semicolon found.
rule_re = re.compile(r'([-a-zA-Z0-9]+)\s*:\s*([^;]+)\s*;?', re.X|re.S|re.M)

# attribute selector regular expression  tag[att=val]
attribute_selector_re = re.compile(
    r'([a-zA-Z0-9-]*)\[([a-zA-Z0-9-]+)=([^]]+)\]:?(\w*)', re.S|re.M)

counter_re = re.compile(r'(^|[^$])[$](\w+)', re.S|re.M)

# all my style objects are really dictionaries -- but I can override as needed
Style = dict
#class Style(dict):
#  def __getattr__(self, attrib):
#    "Called only if the attribute doesn't exist in the class"
#    new_attrib = re.sub('([a-z])([A-Z])',
#        lambda m: ('%s-%s' % m.groups()).lower(), attrib)
#
#    if self.has_key(new_attrib):
#      return self[new_attrib]
#    else:
#      raise AttributeError('%s not found in CSS' % new_attrib)



class CSS(object):
  def __init__(self, filenameortext):
    self.selectors = []
    self.counters = {}

    # file-like object
    if hasattr(filenameortext, 'read'):
      text = filenameortext.read()
    # file
    elif os.path.isfile(filenameortext):
      f = open(filenameortext)
      text = f.read()
      f.close()
    # text
    else:
      text = filenameortext

    self.parse(text)

  def parse(self, text):
    # remove comments
    text = comment_re.sub('', text)

    for match in chunk_re.finditer(text):
      self.selectors.append(Selector(match.group(1), rules=match.group(2)))

  def format(self):
    ret = []
    for sel in self.selectors:
      ret.append(sel.format())

    return '\n\n'.join(ret)
  
  def matches(self, selector):
    """Searches for selectors matching parameter.  Return a list.
    """

    ret = []
    for sel in self.selectors:
      if sel.matches(selector):
        ret.append(sel)

    return ret

  def getrules(self, selector):
    """Returns a dictionary of rules that match the given selector
    """
    rules = Style()
    for sel in self.matches(selector):
      rules.update(sel.rules)

    return rules

  def updatecounters(self, selector):
     """Updates any counters specified in the rules
     """
     for sel in self.matches(selector):
       # reset
       if sel.rules.has_key('counter-reset'):
         ctr = sel.rules['counter-reset']
         self.counters[ctr] = 0
       # increment
       if sel.rules.has_key('counter-increment'):
         ctr = sel.rules['counter-increment']
         self.counters[ctr] = self.counters.get(ctr, 0) + 1
       
  def counterinterpolate(self, content):
    """Takes content and replaces any $counter variables - $$ is a literal $
    """
    # create match function
    def countersub(match):
      # group(1) is a non-$ character or empty
      # group(2) is countername
      return match.group(1) + \
          str(self.counters.get(match.group(2), 'undefined-counter-'+match.group(2)))

    return counter_re.sub(countersub, content)


class Selector(object):
  def __init__(self, selector, rules):
    self.rules = Style()

    # we get a tuple of interesting strings
    self.selector = tuple([s for s in sel_split_re.split(selector) if s]) 

    for match in rule_re.finditer(rules):
      self.rules[match.group(1).strip()] = match.group(2).strip()

  def format(self):
    ret = []

    for rule in self.rules:
      ret.append(rule + ': ' + self.rules[rule] + ';' )

    return ' '.join(self.selector) + ' {\n  ' + '\n  '.join(ret) + '\n}'


  def matches(self, other):
    """Return true if this selector matches other (a CSS selector or an Element list)
    """

    def match(sel, el):
      """Return if the selector piece (sel) matches the element (el)
      """

      # simple case
      if isinstance(el, basestring):
        return sel == el
      
      # this case we have a tuple of ElementTree elements (a trail)
      else:
        # check if we are doing a pseudo element - set to empty string if !exist
        pseudo = el.attrib.get('css:pseudo', '')

        if not pseudo and sel == el.tag:  # simple element selector
          return True
        
        elif sel == el.tag+':'+pseudo:  # element:pseudo selector
          return True

        elif sel.startswith('.'):
          if ':' in sel:  # check if pseudo-selector
            cls, pseudosel = sel.split(':')
          else:
            pseudosel = ''
            cls = sel

          return el.attrib.get('class', None) == cls and pseudosel == pseudo

        elif '.' in sel:
          tag, cls = sel.split('.')

          if ':' in cls:  # check if pseudo-selector
            cls, pseudosel = cls.split(':')
          else:
            pseudosel = ''

          return tag == el.tag and el.attrib.get('class', None) == cls and pseudosel == pseudo

        elif attribute_selector_re.search(sel):
          match = attribute_selector_re.search(sel)
          tag = match.group(1)
          att = match.group(2)
          val = match.group(3)
          pseudosel = match.group(4)

          # now see if we have an actual match
          return el.tag == tag and att in el.attrib and el.attrib[att] == val and pseudosel == pseudo
        else:
          return False

    if isinstance(other, basestring):
      # make into tuple
      other = [s for s in sel_split_re.split(other) if s]

    # we iterate through 2 tuples: the selector tuple and a tuple of strings or
    # Elements
    s_iter = 0  # self.selector iterator
    o_iter = 0  # other iterator
    while s_iter < len(self.selector):
      # iternate through other until we get a match with self.selector
      while o_iter < len(other) \
          and not match(self.selector[s_iter], other[o_iter]):
        o_iter += 1

      # if we iterated past the end of other without a match . . . no match
      if o_iter >= len(other):
        return False

      # now go to next item of self.selector
      s_iter += 1

    # if we got through the loop and:
    # 1. o_iter is at the end of other
    # 2. s_iter is at the end of self.selector 
    #    (always will because of condition of outer loop - so not tested in if)
    # 3. other[o_iter] matches self.selector[s_iter]
    # then then whole selector matched.
    if o_iter == len(other) -1 and match(self.selector[-1], other[o_iter]):
      return True
    else:
      return False

