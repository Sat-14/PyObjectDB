##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import doctest
import tempfile
import unittest

import transaction

import PyObjectDB.config
import PyObjectDB.tests.util
from PyObjectDB.POSException import ReadOnlyError


class ConfigTestBase(PyObjectDB.tests.util.TestCase):
    def _opendb(self, s):
        return PyObjectDB.config.databaseFromString(s)

    def tearDown(self):
        PyObjectDB.tests.util.TestCase.tearDown(self)
        if getattr(self, "storage", None) is not None:
            self.storage.cleanup()

    def _test(self, s):
        db = self._opendb(s)
        try:
            self.storage = db._storage
            # Do something with the database to make sure it works
            cn = db.open()
            rt = cn.root()
            rt["test"] = 1
            transaction.commit()
        finally:
            db.close()


class PyObjectDBConfigTest(ConfigTestBase):
    def test_map_config1(self):
        self._test(
            """
            <PyObjectDB>
              <mappingstorage/>
            </PyObjectDB>
            """)

    def test_map_config2(self):
        self._test(
            """
            <PyObjectDB>
              <mappingstorage/>
              cache-size 1000
            </PyObjectDB>
            """)

    def test_file_config1(self):
        path = tempfile.mktemp()
        self._test(
            """
            <PyObjectDB>
              <filestorage>
                path %s
              </filestorage>
            </PyObjectDB>
            """ % path)

    def test_file_config2(self):
        path = tempfile.mktemp()
        # first pass to actually create database file
        self._test(
            """
            <PyObjectDB>
              <filestorage>
                path %s
              </filestorage>
            </PyObjectDB>
            """ % path)
        # write operations must be disallowed on read-only access
        cfg = """
        <PyObjectDB>
          <filestorage>
            path %s
            create false
            read-only true
          </filestorage>
        </PyObjectDB>
        """ % path
        self.assertRaises(ReadOnlyError, self._test, cfg)

    def test_demo_config(self):
        cfg = """
        <PyObjectDB unused-name>
          <demostorage>
            name foo
            <mappingstorage/>
          </demostorage>
        </PyObjectDB>
        """
        self._test(cfg)


def database_xrefs_config():
    r"""
    >>> db = PyObjectDB.config.databaseFromString(
    ...    "<PyObjectDB>\n<mappingstorage>\n</mappingstorage>\n</PyObjectDB>\n")
    >>> db.xrefs
    True
    >>> db = PyObjectDB.config.databaseFromString(
    ...    "<PyObjectDB>\nallow-implicit-cross-references true\n"
    ...    "<mappingstorage>\n</mappingstorage>\n</PyObjectDB>\n")
    >>> db.xrefs
    True
    >>> db = PyObjectDB.config.databaseFromString(
    ...    "<PyObjectDB>\nallow-implicit-cross-references false\n"
    ...    "<mappingstorage>\n</mappingstorage>\n</PyObjectDB>\n")
    >>> db.xrefs
    False
    """


def dummy_class_factory(connection, module_name, global_name):
    """Helper function for database_class_factory_config
    """


def database_class_factory_config():
    r"""The class-factory option sets the class factory used for
    deserializing persistent objects.

    Without it, the default DB.classFactory method is used:

    >>> db = PyObjectDB.config.databaseFromString(
    ...    "<PyObjectDB>\n<mappingstorage>\n</mappingstorage>\n</PyObjectDB>\n")
    >>> import types
    >>> isinstance(db.classFactory, types.MethodType)
    True
    >>> db.close()

    With a dotted name, the specified callable is used:

    >>> db = PyObjectDB.config.databaseFromString(
    ...    "<PyObjectDB>\nclass-factory PyObjectDB.tests.testConfig.dummy_class_factory\n"
    ...    "<mappingstorage>\n</mappingstorage>\n</PyObjectDB>\n")
    >>> db.classFactory is dummy_class_factory
    True

    The factory is available to connections, including the one
    pooled during __init__:

    >>> conn = db.open()
    >>> conn._reader._factory is dummy_class_factory
    True
    >>> conn.close()
    >>> db.close()

    When the class factory is set to a non-existent callable, a detailed
    error is raised:
    >>> db = PyObjectDB.config.databaseFromString(
    ...    "<PyObjectDB>\n"
    ...     "class-factory PyObjectDB.tests.testConfig.non_existent_class_factory\n"
    ...    "<mappingstorage>\n</mappingstorage>\n</PyObjectDB>\n"
    ... )  # doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ZConfig.DataConversionError: The object named by 'PyObjectDB.tests.testConfig.non_existent_class_factory' could not be imported
    Traceback (most recent call last):
    ...
    """  # noqa: E501


def multi_atabases():
    r"""If there are multiple codb sections -> multidatabase

    >>> db = PyObjectDB.config.databaseFromString('''
    ... <PyObjectDB>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... <PyObjectDB Foo>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... <PyObjectDB>
    ...    database-name Bar
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... ''')
    >>> sorted(db.databases)
    ['', 'Bar', 'foo']

    >>> db.database_name
    ''
    >>> db.databases[db.database_name] is db
    True
    >>> db.databases['foo'] is not db
    True
    >>> db.databases['Bar'] is not db
    True
    >>> db.databases['Bar'] is not db.databases['foo']
    True

    Can't have repeats:

    >>> PyObjectDB.config.databaseFromString('''
    ... <PyObjectDB 1>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... <PyObjectDB 1>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... <PyObjectDB 1>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... ''') # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ZConfig.ConfigurationSyntaxError:
    section names must not be re-used within the same container:'1' (line 9)

    >>> PyObjectDB.config.databaseFromString('''
    ... <PyObjectDB>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... <PyObjectDB>
    ...    <mappingstorage>
    ...    </mappingstorage>
    ... </PyObjectDB>
    ... ''') # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
    ...
    ValueError: database_name '' already in databases

    """


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(
        setUp=PyObjectDB.tests.util.setUp,
        tearDown=PyObjectDB.tests.util.tearDown,
        checker=PyObjectDB.tests.util.checker))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(
        PyObjectDBConfigTest))
    return suite
