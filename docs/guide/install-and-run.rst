===========================
Installing and running PyObjectDB
===========================

This topic discusses some boring nitty-gritty details needed to
actually run PyObjectDB.

Installation
============

Installation of PyObjectDB is pretty straightforward using Python's
packaging system. For example, using pip::

  pip install PyObjectDB

You may need additional optional packages, such as `ZEO
<https://pypi.org/project/ZEO/>`_ or `RelStorage
<https://pypi.org/project/RelStorage/>`_, depending your deployment
choices.

Configuration
=============

You can set up PyObjectDB in your application using either Python, or
PyObjectDB's configuration language.  For simple database setup, and
especially for exploration, the Python APIs are sufficient.

For more complex configurations, you'll probably find PyObjectDB's
configuration language easier to use.

To understand database setup, it's important to understand PyObjectDB's
architecture.  PyObjectDB separates database functionality
from storage concerns. When you create a database object,
you specify a storage object for it to use, as in::

    import PyObjectDB, PyObjectDB.FileStorage

    storage = PyObjectDB.FileStorage.FileStorage('mydata.fs')
    db = PyObjectDB.DB(storage)

So when you define a database, you'll also define a storage. In the
example above, we define a :class:`file storage
<PyObjectDB.FileStorage.FileStorage.FileStorage>` and then use it to define
a database.

Sometimes, storages are created through composition.  For example, if
we want to save space, we could layer a ``ZlibStorage``
[#zlibstoragefn]_ over the file storage::

    import PyObjectDB, PyObjectDB.FileStorage, zc.zlibstorage

    storage = PyObjectDB.FileStorage.FileStorage('mydata.fs')
    compressed_storage = zc.zlibstorage.ZlibStorage(storage)
    db = PyObjectDB.DB(compressed_storage)

`ZlibStorage <https://pypi.org/project/zc.zlibstorage/>`_
compresses database records [#zlib]_.

Python configuration
--------------------

To set up a database with Python, you'll construct a storage using the
:ref:`storage APIs <included-storages-label>`, and then pass the
storage to the :class:`~PyObjectDB.DB` class to create a database, as shown
in the examples in the previous section.

The :class:`~PyObjectDB.DB` class also accepts a string path name as its
storage argument to automatically create a file storage.  You can also
pass ``None`` as the storage to automatically use a
:class:`~PyObjectDB.MappingStorage.MappingStorage`, which is convenient when
exploring PyObjectDB::

  db = PyObjectDB.DB(None) # Create an in-memory database.

Text configuration
------------------

PyObjectDB supports a text-based configuration language.  It uses a syntax
similar to Apache configuration files.  The syntax was chosen to be
familiar to site administrators.

PyObjectDB's text configuration uses `ZConfig
<https://pypi.org/project/ZConfig/>`_. You can use ZConfig to
create your application's configuration, but it's more common to
include PyObjectDB configuration strings in their own files or embedded in
simpler configuration files, such as `configarser
<https://docs.python.org/3/library/configparser.html#module-configparser>`_
files.

A database configuration string has a ``PyObjectDB`` section wrapping a
storage section, as in::

  <PyObjectDB>
    cache-size-bytes 100MB
    <mappingstorage>
    </mappingstorage>
  </PyObjectDB>

.. -> snippet

In the example above, the :ref:`mappingstorage
<mappingstorage-text-configuration>` section defines the storage used
by the database.

To create a database from a string, use
:func:`PyObjectDB.config.databaseFromString`::

    >>> import PyObjectDB.config
    >>> db = PyObjectDB.config.databaseFromString(snippet)

To load databases from file names or URLs, use
:func:`PyObjectDB.config.databaseFromURL`.

URI-based configuration
-----------------------

Another database configuration option is provided by the `PyObjectDBuri
<https://pypi.org/project/PyObjectDBuri/>`_ package. See:
http://docs.pylonsproject.org/projects/PyObjectDBuri.  It's less powerful
than the Python or text configuration options, but allows
configuration to be reduced to a single URI and handles most cases.

Using databases: connections
============================

Once you have a database, you need to get a database connection to do
much of anything.  Connections take care of loading and saving objects
and manage object caches. Each connection has its own cache
[#caches-are-expensive]_.

.. _getting-connections:

Getting connections
-------------------

Amongst [#amongst]_ the common ways of getting a connection:

db.open()
   The database :meth:`~PyObjectDB.DB.open` method opens a
   connection, returning a connection object::

      >>> conn = db.open()

   It's up to the application to call
   :meth:`~PyObjectDB.Connection.Connection.close` when the application is
   done using the connection.

   If changes are made, the application :ref:`commits transactions
   <using-transactions-label>` to make them permanent.

db.transaction()
   The database :meth:`~PyObjectDB.DB.transaction` method
   returns a context manager that can be used with the `python with
   statement
   <https://docs.python.org/3/reference/compound_stmts.html#grammar-token-with_stmt>`_
   to execute a block of code in a transaction::

     with db.transaction() as connection:
         connection.root.foo = 1

   .. -> src

      >>> exec(src)
      >>> with db.transaction() as connection:
      ...     print(connection.root.foo)
      1

      >>> _ = conn.transaction_manager.begin() # get updates on conn

   In the example above, we used ``as connection`` to get the database
   connection used in the variable ``connection``.

some_object._p_jar
   For code that's already running in the context of an open
   connection, you can get the current connection as the ``_p_jar``
   attribute of some persistent object that was accessed via the
   connection.

Getting objects
---------------

Once you have a connection, you access objects by traversing the
object graph from the root object.

The database root object is a mapping object that holds the top level
objects in the database.  There should only be a small number of
top-level objects (often only one).  You can get the root object by calling a
connection's ``root`` attribute::

    >>> root = conn.root()
    >>> root
    {'foo': 1}
    >>> root['foo']
    1

For convenience [#root-convenience]_, you can also get top-level
objects by accessing attributes of the connection root object:

    >>> conn.root.foo
    1

Once you have a top-level object, you use its methods, attributes, or
operations to access other objects and so on to get the objects you
need.  Often indexing data structures like BTrees_ are used to
make it possible to search objects in large collections.

.. [#zlibstoragefn] `zc.zlibstorage
   <https://pypi.org/project/zc.zlibstorage/>`_ is an optional
   package that you need to install separately.

.. [#zlib] ZlibStorage uses the :mod:`zlib` standard module, which
   uses the `zlib library <http://www.zlib.net/>`_.

.. [#caches-are-expensive] PyObjectDB can be very efficient at caching data
   in memory, especially if your `working set
   <https://en.wikipedia.org/wiki/Working_set>`_ is small enough to
   fit in memory, because the cache is simply an object tree and
   accessing a cached object typically requires no database
   interaction.  Because each connection has its own cache,
   connections can be expensive, depending on their cache sizes.  For
   this reason, you'll generally want to limit the number of open
   connections you have at any one time.  Connections are pooled, so
   opening a connection is inexpensive.

.. [#amongst] https://www.youtube.com/watch?v=7WJXHY2OXGE

.. [#root-convenience] The ability to access top-level objects of the
   database as root attributes is a recent convenience. Originally,
   the ``root()`` method was used to access the root object which was
   then accessed as a mapping.  It's still potentially useful to
   access top-level objects using the mapping interface if their names
   aren't valid attribute names.

.. _BTrees: https://pythonhosted.org/BTrees/
