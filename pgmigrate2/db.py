from sqlalchemy import create_engine, Table, MetaData, Column, String, sql
from sqlalchemy.sql.expression import text
import sqlalchemy.exc

metadata = MetaData()

applied_patches_table = Table('__applied_patches__', metadata,
   Column('id', String(36), primary_key=True),
)

class Db(object):
    def __init__(self, url):
        self.url = url
        self.engine = create_engine(self.url)
        self.connection = self.engine.connect()
        
    def init(self):
        metadata.create_all(self.engine) 
        
    def test(self, repo):
        unapplied = self._find_unapplied(repo)
        for patch in unapplied:
            print 'Need to apply: %s' % patch.memo
        
        if not unapplied:
            print "All patches are already applied."
        return bool(unapplied)
        
    def migrate(self, repo):
        unapplied = self._find_unapplied(repo)
        
        if unapplied:
            print "Need to apply %d patches:" % len(unapplied)
        else:
            print "All patches are already applied."
            return True
        
        for patch in unapplied:
            try:
                self.engine.transaction(self._patch, patch)
            except sqlalchemy.exc.ProgrammingError, e:
                print "Failed: %s" % e.message
                return False
            
        return True
                
    def _find_unapplied(self, repo):
        applied = set(x.id for x in self.engine.execute(sql.select([applied_patches_table.c.id])))

        return [x for x in repo.patches if x.id not in applied]        
                
    def _patch(self, conn, patch):
        print "Applying '%s'" % patch.memo
        conn.execute(text(patch.sql))
        
        ins = applied_patches_table.insert().values(id=patch.id)
        conn.execute(ins)
        
