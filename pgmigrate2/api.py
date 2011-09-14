from __future__ import with_statement
import os
import uuid
import tempfile
import codecs
import subprocess
import getpass
import datetime

from pgmigrate2.db import Db
from pgmigrate2.repo import PatchRepo, Patch

def init_db(db_url):
    db = Db(db_url)
    db.init()


def check_status(repo_path, db_url):
    pr = PatchRepo(repo_path)
    db = Db(db_url)

    result = db.test(pr)
    return 0 if result else 1
    

def migrate(repo_path, db_url):
    pr = PatchRepo(repo_path)
    db = Db(db_url)
    
    result = db.migrate(pr)
    return 0 if result else 1


def newpatch(repo_path):
    pr = PatchRepo(repo_path)
    patch = read_patch()
    if not patch:
        return
    path = pr.add_patch(patch)
    print "Wrote '%s'" % path
    return path    


def get_blank_slate(change_id):    
    return ('\n'            
            '\n'
            '--- Memo: \n'
            '\n'
            '--- PG: Enter SQL snippet which does schema migration. Leave empty snippet to abort.\n'
            '--- PG: Lines starting with \'PG:\' will be removed\n'
            '--- PG: migration: %(change_id)s\n'
            '') % locals()

def geteditor():
    '''return editor to use'''
    return (os.environ.get("HGEDITOR") or
            os.environ.get("VISUAL") or
            os.environ.get("EDITOR", "editor"))
   
def read_patch():
    change_id = str(uuid.uuid1())
    slate = get_blank_slate(change_id)
    _, fpath = tempfile.mkstemp('.sql', 'pgmigrate2', text=True)
    
    try:    
        with codecs.open(fpath, 'wt', encoding='utf-8') as f:
            f.write(slate)
            
        subprocess.check_call('%s %s' % (geteditor(), fpath), shell=True)
        
        with codecs.open(fpath, 'rt', encoding='utf-8') as f:
            content = f.read()
            if content == slate:
                return
    finally:
        os.unlink(fpath)
        
    memo = ''
    sql_bits = []
    for l in content.splitlines():
        if l.startswith('--- Memo:'):
            memo = l[len('--- Memo:'):].strip()
        elif not l.startswith('--- PG: '):
            sql_bits.append(l)
            
    return Patch(id=change_id, date=datetime.datetime.now(), author=getpass.getuser(), memo=memo, sql='\n'.join(sql_bits))

