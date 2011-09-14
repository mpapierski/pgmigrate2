from __future__ import with_statement
import os
import re
import codecs
import datetime
import unicodedata

class Patch(object):
    def __init__(self, id, author, memo, sql, date=None):
        self.id = id
        self.date = date
        self.author = author
        self.memo = memo
        self.sql = sql
        
    def __repr__(self):
        return 'Patch(%r, %r, %r, %r, %r)' % (self.id, self.date, self.author, self.memo, self.sql)


patch_filename_re = re.compile('^(?P<seq>\d+)_(.+)\.sql$')
patch_re = re.compile('---\s*id:\s*(?P<id>.+?)\n'
                      '---\s*author:\s*(?P<author>.+?)\n'
                      '---\s*memo:\s*(?P<memo>.+?)\n'
                      '(---\s*date:\s*(?P<date>.+?)\n)?'
                      '(?P<sql>.+)', re.DOTALL)

class PatchRepo(object):
    def __init__(self, path):
        self.path = path
        self.seq = 0
        self.patches = []
        self.refresh()
        
    def refresh(self):
        self.seq = 0
        self.patches = []
        for fn in sorted(os.listdir(self.path)):
            match = patch_filename_re.match(fn)
            if not match:
                continue
            
            seq = int(match.group('seq'))
            self.seq = max(self.seq, seq)
            
            with open(os.path.join(self.path, fn), 'rt') as f:
                content = f.read()
                match = patch_re.search(content)
                if not match:
                    print "Unable to parse %s" % fn
                    continue
                
                date = None
                if match.group('date'):
                    date = datetime.datetime.strptime(match.group('date'), "%Y-%m-%d %H:%M")
                
                p = Patch(id=match.group('id'),
                          author=match.group('author'),
                          memo=match.group('memo'),
                          sql=match.group('sql').strip(),
                          date=date
                          )
                self.patches.append(p)
    
    def add_patch(self, patch):
        self.seq += 1
        fn = '%06d_%s.sql' % (self.seq, memo_to_fn(patch.memo))
        fpath = os.path.join(self.path, fn)
        with codecs.open(fpath, 'wt', encoding='utf-8') as f:
            f.write('--- id:      %s\n'
                    '--- author:  %s\n'
                    '--- memo:    %s\n'
                    '--- date:    %s\n'
                    '\n'
                    '%s' % (patch.id, 
                                 patch.author,
                                 patch.memo,
                                 patch.date.strftime("%Y-%m-%d %H:%M"),
                                 patch.sql))
            
        return fpath


def memo_to_fn(x):
    bits = []
    print x
    for l in x:
        if 'LETTER' in unicodedata.name(l):
            bits.append(l)
        elif 'DIGIT' in unicodedata.name(l):
            bits.append(l)
        elif bits[-1] != '_':
            bits.append('_')
    return ''.join(bits)
