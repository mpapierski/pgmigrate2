import argparse
from pgmigrate2 import api
import sys



def init(args):
    api.init_db(args.DBURL)
    
def migrate(args):
    return api.migrate(args.REPO, args.DBURL)

def check(args):
    return api.check_status(args.REPO, args.DBURL)
    
def newpatch(args):
    return api.newpatch(args.REPO)

def main():
    parser = argparse.ArgumentParser(description='Database Migrations.')
    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands')
    
    parser_init = subparsers.add_parser('init', help='Initialize database with migration tracking.')
    parser_init.add_argument('DBURL', type=str, help='database connection URL')
    parser_init.set_defaults(func=init)

    parser_patch = subparsers.add_parser('newpatch', help='Create a new patch')
    parser_patch.add_argument('REPO', type=str, help='path to patch repo')
    parser_patch.set_defaults(func=newpatch)

    parser_check = subparsers.add_parser('check', help='Check migration status')
    parser_check.add_argument('REPO', type=str, help='path to patch repo')
    parser_check.add_argument('DBURL', type=str, help='database connection URL')
    parser_check.set_defaults(func=check)

    parser_migrate = subparsers.add_parser('migrate', help='Apply outstanding migrations')
    parser_migrate.add_argument('REPO', type=str, help='path to patch repo')
    parser_migrate.add_argument('DBURL', type=str, help='database connection URL')
    parser_migrate.add_argument('--dry-run', action='store_true', default=False, help='do not change anything')
    parser_migrate.set_defaults(func=migrate)

    
    args = parser.parse_args()
    
    retcode = args.func(args)
     
    sys.exit(retcode or 0)    
    
if __name__ == '__main__':
    main()    