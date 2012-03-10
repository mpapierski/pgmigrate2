======================================================
Painless DVCS-aware database migrations for PostgreSQL
======================================================

Theory
------

PGmigrate helps you to evolve your database together with your application. 
The core fundamental unit of PGmigrate is a single SQL snippet called 'patch'.

Sample db patch::

   serg@t420s:~/projects/shopium/migrations[hg:default] $ cat 000049_Added_index_on_CategorySlug.sql 
   --- id:      89ccfca6-6851-11e1-99d8-a088b4e3b168
   --- author:  serg
   --- memo:    Added index on CategorySlug
   --- date:    2012-03-07 14:32
   
   CREATE UNIQUE INDEX catalog_category_slug_shop_id_slug
     ON catalog_category_slug
     USING btree
     (shop_id, slug);
   
As you can see patch is a valid SQL file, which can be executed directly. 


Quickstart
----------

Initialize database
^^^^^^^^^^^^^^^^^^^

::

    $ pgmigrate2 init postgresql://user@password/testdb
    $
   
This will create table `__applied_patches__` in testdb. This table is used to track which patches are already applied.


Create a patch repo, and a first patch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::
   
    $ mkdir patchrepo
    $ pgmigrate2 newpatch patchrepo
    ... edit patch in your text editor...
    Wrote 'patchrepo/000001_creating_table_x.sql'
    $
   
This will create empty patch and open it in your text editor. Enter patch SQL, and optional memo, describing what is the function of this patch.

PGmigrate will create a file like `patchrepo/000001_creating_table_x.sql` where `000001` is a patch serial number, and `creating_table_x` is a 
slugified patch memo.

   
Check what needs to be applied to
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    $ pgmigrate2 check patchrepo/ postgresql://user@password/testdb
    Need to apply: creating table x
    $

Check takes all patches in patch repo, and print a list of patches which are need to be applied to testd.


Apply patches
^^^^^^^^^^^^^

::

   $ pgmigrate2 migrate patchrepo/ postgresql://user@password/testdb
   Need to apply 1 patches:
   Applying 'creating table x'
   $ 

Migrate takes all patches from patch repo, and sequentially applies those of them, whose id are not present in `__applied_patches__`
tables of `testdb`.


Embedding
---------

Here is example how we use PGmigrate in our project::

   ### Database migration commands
   @finaloption.command(config_opts)
   def dbmigrate(config):
       from shopium.core.config import read_config
       config = read_config(config)
       from pgmigrate2 import api
       
       return api.migrate('migrations', config.db_uri)
   

   @finaloption.command(config_opts)
   def dbnewpatch(config):
       from shopium.core.config import read_config
       config = read_config(config)
       from pgmigrate2 import api
       
       import subprocess
       
       path = api.newpatch('migrations')
       if path:
           subprocess.check_call('hg add %s' % path, shell=True) # add just created patch to Mercurial


   @finaloption.command(config_opts)
   def dbcheckstatus(config):
       from shopium.core.config import read_config
       config = read_config(config)
       from pgmigrate2 import api
       
       api.check_status('migrations', config.db_uri)


Q&A
---

Why snippets contain SQL instead of programs in some DSL?
   We belive that it if you have a good developers — it makes no sense to hide 
   power to SQL from them. So, with PGmigrate you have a full control on what would be executed.
   Also since we do not have any fancy stuff, PGmigrate is quite simple, and can be used in almost any development model.  
