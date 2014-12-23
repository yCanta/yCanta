# -*- coding: utf-8 -*-
"""Setup the yCanta application"""
from __future__ import print_function
import warnings
warnings.resetwarnings()
warnings.simplefilter('error')

import logging
from tg import config
from ycanta import model
import transaction

def bootstrap(command, conf, vars):
    """Place any commands to setup ycanta here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        u = model.User()
        u.user_name = u'manager'
        u.display_name = u'Example manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'managepass'
    
        model.DBSession.add(u)
    
        g = model.Group()
        g.group_name = u'managers'
        g.display_name = u'Managers Group'
    
        g.users.append(u)
    
        model.DBSession.add(g)
    
        p = model.Permission()
        p.permission_name = u'manage'
        p.description = u'This permission give an administrative right to the bearer'
        p.groups.append(g)
    
        model.DBSession.add(p)
    
        u1 = model.User()
        u1.user_name = u'editor'
        u1.display_name = u'Example editor'
        u1.email_address = u'editor@somedomain.com'
        u1.password = u'editpass'
    
        model.DBSession.add(u1)
        model.DBSession.flush()
        transaction.commit()

    except IntegrityError:
        print('Warning, there was a problem adding your auth data, it may have already been added:')
        import traceback
        print(traceback.format_exc())
        transaction.abort()
        print('Continuing with bootstrapping...')

    print()
    print('Adding songs ...')
    import glob
    import ycanta.lib.song
    count = 0
    for songfile in glob.glob('songs/*'):
      song = model.Song.load_from_file(songfile)
      model.DBSession.add(song)
      count += 1

    model.DBSession.flush()
    transaction.commit()

    # <websetup.bootstrap.after.auth>
