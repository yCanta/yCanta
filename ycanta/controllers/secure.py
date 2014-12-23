# -*- coding: utf-8 -*-
"""Sample controller with all its actions protected."""
from tg import expose, flash
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.predicates import has_permission
from ycanta import model
from ycanta.lib.base import BaseController

__all__ = ['SecureController']

class SecureController(BaseController):
    """Sample controller-wide authorization"""
    
    # The predicate that must be met for all the actions in this controller:
    #allow_only = has_permission('manage',
    #                            msg=l_('Only for people with the "manage" permission'))
    
    
    @expose()  #self is sb, 
    def _lookup(self, *args):
        print args
        if len(args) == 0:
            pass
        elif len(args) <= 2:   #book with name and/or edit, pdf, present, etc
            print args[1:]
            return BookController(args[0]), args[1:]
        elif len(args) <= 4:   #song with name and/or edit, pdf, etc 
            print args[3:]
            return SongController(args[0], args[2]), args[3:]

        return BookController('controller'), []


class BookController(object):
    def __init__(self, name):             #creating a new book
        self.book = model.Book(title='Book1', content='<xml><songref status="n" ref="songs/1355104343.14-down-in-the-valley.song"/></xml>')
        pass

    @expose('ycanta.templates.book')
    def index(self):                      #viewing songbook 
        return dict(book=self.book, breadcrumbs = [[self.book.title,'book/'+self.book.title]], page_content = "this", l_panel="this is the left panel", r_panel="this is the right one!")

    @expose('ycanta.templates.book_edit')
    def edit(self):
        return dict()

    @expose('ycanta.templates.pdf')
    def pdf(self):
        return dict()

    @expose('ycanta.templates.present')
    def present(self):
        return dict()

    @expose()
    def delete(self):
        return dict()

class SongController(object):
    def __init__(self, book, name):    #creating a new song
        self.book = model.Book.all_songs_book()
        
        song_id = name.split('-')[0]
        self.song = model.DBSession.query(model.Song).get(song_id)
        if self.song == None:          #we have an invalid song_id, error handling goes below here
          pass

    @expose('ycanta.templates.song')
    def index(self):                   #viewing song
        song = self.song
        book = self.book
        breadcrumbs = [[book.title,'book/'+ book.title],
                  [song.title, 'book/'+book.title+'/song/'+str(song.id)+'-'+song.title]]

        return dict(song=self.song, book=self.book, breadcrumbs = breadcrumbs, page_content = "this", l_panel="this is the left panel", r_panel="this is the right one!")

    @expose('ycanta.templates.song_edit')
    def edit(self):
        return dict()

    @expose('ycanta.templates.pdf')
    def pdf(self):
        return dict()

    @expose()
    def delete(self):
        return dict()


 #   @expose('ycanta.templates.index')
 #   def index(self):
 #"""Let the user know that's visiting a protected controller."""
 #   flash(_("Secure Controller here"))
 #       return dict(page='index')
 #   
 #   @expose('ycanta.templates.index')
 #   def some_where(self):
 #       """Let the user know that this action is protected too."""
 #       return dict(page='some_where')
