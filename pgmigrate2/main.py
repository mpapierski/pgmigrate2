import argparse
import tempfile
import os
import uuid
import codecs
import string
import getpass
import datetime
import subprocess
from pgmigrate2.repo import Patch, PatchRepo
from pgmigrate2.db import Db
import sys


def get_blank_slate(change_id):    
    return ('\n'            
            '\n'
            '--- Memo: \n'
            '\n'
            '--- PG: Enter SQL snippet which does schema migration. Leave empty snippet to abort.\n'
            '--- PG: Lines starting with \'PG:\' will be removed\n'
            '--- PG: migration: %(change_id)s\n'
            '') % locals()

def read_patch():
    change_id = str(uuid.uuid1())
    slate = get_blank_slate(change_id)
    _, fpath = tempfile.mkstemp('.sql', 'pgmigrate2', text=True)
    try:    
        with codecs.open(fpath, 'wt', encoding='utf-8') as f:
            f.write(slate)
            
        subprocess.check_call('editor %s' % fpath, shell=True)
        
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


def init(args):
    db = Db(args.URL)
    db.init()
    
def migrate(args):
    pr = PatchRepo(args.REPO)
    db = Db(args.URL)
    
    result = db.migrate(pr)
    return 0 if result else 1

def test(args):
    pr = PatchRepo(args.REPO)
    db = Db(args.URL)
    
    result = db.test(pr)
    return 0 if result else 1

def patch(args):
    pr = PatchRepo(args.REPO)
    patch = read_patch()
    if not patch:
        #print "Cancelled"
        return
    pr.add_patch(patch)
    print "Done"    

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    
    # create the parser for the "a" command
    parser_init = subparsers.add_parser('init', help='init help')
    parser_init.add_argument('URL', type=str, help='bar help')
    parser_init.set_defaults(func=init)

    parser_test = subparsers.add_parser('test', help='init help')
    parser_test.add_argument('URL', type=str, help='bar help')

    parser_patch = subparsers.add_parser('patch', help='patch help')
    parser_patch.add_argument('REPO', type=str, help='path to patch repo')
    parser_patch.set_defaults(func=patch)
    #parser_test.add_argument('URL', type=str, help='bar help')

    parser_test = subparsers.add_parser('test', help='test help')
    parser_test.add_argument('REPO', type=str, help='path to patch repo')
    parser_test.add_argument('URL', type=str, help='DB url')
    parser_test.set_defaults(func=test)

    parser_migrate = subparsers.add_parser('migrate', help='migrate help')
    parser_migrate.add_argument('REPO', type=str, help='path to patch repo')
    parser_migrate.add_argument('URL', type=str, help='DB url')
    parser_migrate.set_defaults(func=migrate)

    
    args = parser.parse_args()
    
    retcode = args.func(args)
     
    sys.exit(retcode or 0)    
    
if __name__ == '__main__':
    main()    