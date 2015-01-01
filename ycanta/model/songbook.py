# -*- coding: utf-8 -*-
"""Sample model module."""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, UnicodeText, DateTime
from sqlalchemy.ext.declarative import declared_attr
#from sqlalchemy.orm import relation, backref

from ycanta.model import DeclarativeBase, metadata, DBSession
from ycanta.model.auth import User

import ycanta.lib.song


class LastModifiedMixin(object):
  @declared_attr
  def last_modified_who(cls):
    return Column(ForeignKey(User.user_id))
  last_modified_ts  = Column(DateTime, default=func.now())

class Book(LastModifiedMixin, DeclarativeBase):
  __tablename__ = 'book'
  
  id            = Column(Integer, primary_key=True)
  title         = Column(Unicode(), nullable=False, unique=True)
  content       = Column(UnicodeText(), nullable=False) # space separated list of ids
  configuration = Column(UnicodeText(), nullable=True)  # JSON data {'config name': '--string', 'config2': '...' }
  
  ALL_SONGS_TITLE = u'All Songs'

  def repr(self):
    return '<Book: id=%s title=%s>' % (repr(self.id), repr(self.title))

  def songs(self):
    """Returns a list of Song objects in this Book"""
    return DBSession.query(Song).filter(Song.id.in_(self.content.split()))

  def get_configs(self):
    """Returns a list of configs"""
    # TODO: actually implement
    return [
        dict(name='Config name', config='--index-cat-exclude Needs,Duplicate --small-size 4 --display-scrip-index no-page-break --font-face Helvetica --start-song-on-new-page no --song-space-after 6 --small-space 4 --display-index no-page-break --songtitle-space 4 --paper-orientation landscape --index-title-space 2 --songchunk-b4 6 --index-cat-font Helvetica --paper-margin-top 0.5 --page-margin-right 0.1 --resize-percent 100 --index-cat-b4 12 --copyright-space-b4 1 --paper-margin-bottom 0.5 --display-cat-index on-new-page --page-margin-bottom 0.1 --hide-booktitle no --page-layout single-sided --index-title-b4 30 --scripture-location under-title --songline-size 6 --songchord-space 1 --index-song-font Helvetica-Bold --songchord-size 6 --page-margin-left 0.1 --columns 5 --songline-space 2 --copyright-size 4 --index-song-size 6 --index-title-size 10 --index-cat-size 8 --songtitle-size 8 --paper-margin-left 0.5 --page-margin-top 0.1 --display-chords no --songtitle-format $num\s --index-first-line-font Helvetica-Oblique --index-first-line-space 2 --index-song-space 2 --binder-margin 0 --ccli None --index-cat-space 2 --paper-margin-right 0.5 --index-first-line-size 6 --paper-size letter --index-title-font Helvetica --booktitle-size 12 --booktitle-space 3 --print_a checked --print_n checked'),
      ]

  @classmethod
  def get_global_configs(clas):
    """Same format as book.get_configs()"""
    return [
        dict(name='Global cfg', config='--index-cat-exclude Needs,Duplicate --small-size 4 --display-scrip-index no-page-break --font-face Helvetica --start-song-on-new-page no --song-space-after 6 --small-space 4 --display-index no-page-break --songtitle-space 4 --paper-orientation landscape --index-title-space 2 --songchunk-b4 6 --index-cat-font Helvetica --paper-margin-top 0.5 --page-margin-right 0.1 --resize-percent 100 --index-cat-b4 12 --copyright-space-b4 1 --paper-margin-bottom 0.5 --display-cat-index on-new-page --page-margin-bottom 0.1 --hide-booktitle no --page-layout single-sided --index-title-b4 30 --scripture-location under-title --songline-size 6 --songchord-space 1 --index-song-font Helvetica-Bold --songchord-size 6 --page-margin-left 0.1 --columns 5 --songline-space 2 --copyright-size 4 --index-song-size 6 --index-title-size 10 --index-cat-size 8 --songtitle-size 8 --paper-margin-left 0.5 --page-margin-top 0.1 --display-chords no --songtitle-format $num\s --index-first-line-font Helvetica-Oblique --index-first-line-space 2 --index-song-space 2 --binder-margin 0 --ccli None --index-cat-space 2 --paper-margin-right 0.5 --index-first-line-size 6 --paper-size letter --index-title-font Helvetica --booktitle-size 12 --booktitle-space 3 --print_a checked --print_n checked'),
      ]

  @classmethod
  def all_songs_book(clas):
    return Book(
        title=Book.ALL_SONGS_TITLE,
        content=u' '.join(unicode(s.id) for s in DBSession.query(Song.id).order_by(Song.title)))


class BookHistory(LastModifiedMixin, DeclarativeBase):
  __tablename__ = 'book_history'

  id      = Column(Integer, primary_key=True)
  book_id = Column(ForeignKey(Book.id))
  content = Column(UnicodeText(), nullable=False)


song_category_association_table = Table('association', DeclarativeBase.metadata,
        Column('category_id', Integer, ForeignKey('category.id')),
        Column('song_id',     Integer, ForeignKey('song.id')))


class Category(DeclarativeBase):
  __tablename__ = 'category'

  id    = Column(Integer, primary_key=True)
  name  = Column(Unicode(), nullable=False)
  songs = relationship('Song', 
          secondary=song_category_association_table, 
          backref='categories')


class Song(LastModifiedMixin, DeclarativeBase):
  __tablename__ = 'song'

  id           = Column(Integer, primary_key=True)
  title        = Column(Unicode(), nullable=False)
  author       = Column(Unicode(), nullable=False)
  scripture    = Column(Unicode(), nullable=True)
  introduction = Column(Unicode(), nullable=True)
  key          = Column(Unicode(), nullable=True)
  ccli         = Column(Boolean(), nullable=False)
  copyright    = Column(Unicode(), nullable=True)
  content      = Column(UnicodeText(), nullable=False)
  
  def repr(self):
    return '<Song: id=%s title=%s author=%s>' % (repr(self.id), repr(self.title), repr(self.author))

  def toxmlstr(self):
    return ycanta.lib.song.song_to_str(self)

  def toxmlET(self):
    return ycanta.lib.song.song_to_ET(self)

  def tosearchstr(self):
    def ensure_str(s, default):
      if not isinstance(s, basestring):
        return default
      return s

    ret = u't:%s; ' % self.title
    ret += u' '.join('a:%s; ' % a for a in ensure_str(self.author, '!a').split(','))
    if len(self.categories):
      ret += u' '.join('c:%s; ' % c.name for c in self.categories)
    else:
      ret += u'c:!c'
    ret += u'\n'.join(ycanta.lib.song.song_chunks_to_mono(self, exclude_chords=True))
    return ret

  @classmethod
  def load_from_file(clas, filename):
    return ycanta.lib.song.load(filename)


class SongHistory(LastModifiedMixin, DeclarativeBase):
  __tablename__ = 'song_history'

  id      = Column(Integer, primary_key=True)
  song_id = Column(ForeignKey(Song.id))
  content = Column(UnicodeText(), nullable=False)


