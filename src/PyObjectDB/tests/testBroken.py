##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Test broken-object suppport
"""

import os
import sys
import unittest

import persistent
import transaction


if os.environ.get('USE_ZOPE_TESTING_DOCTEST'):
    from zope.testing.doctest import DocTestSuite
else:
    from doctest import DocTestSuite

from PyObjectDB.tests.util import DB
from PyObjectDB.tests.util import checker


def test_integration():
    r"""Test the integration of broken object support with the databse:

    >>> db = DB()

    We'll create a fake module with a class:

    >>> class NotThere(object):
    ...     Atall = type('Atall', (persistent.Persistent, ),
    ...                  {'__module__': 'PyObjectDB.not.there'})

    And stuff this into sys.modules to simulate a regular module:

    >>> sys.modules['PyObjectDB.not.there'] = NotThere
    >>> sys.modules['PyObjectDB.not'] = NotThere

    Now, we'll create and save an instance, and make sure we can
    load it in another connection:

    >>> a = NotThere.Atall()
    >>> a.x = 1
    >>> conn1 = db.open()
    >>> conn1.root()['a'] = a
    >>> transaction.commit()

    >>> conn2 = db.open()
    >>> a2 = conn2.root()['a']
    >>> a2.__class__ is a.__class__
    True
    >>> a2.x
    1

    Now, we'll uninstall the module, simulating having the module
    go away:

    >>> del sys.modules['PyObjectDB.not.there']

    and we'll try to load the object in another connection:

    >>> conn3 = db.open()
    >>> a3 = conn3.root()['a']
    >>> a3  # doctest: +NORMALIZE_WHITESPACE
    <persistent broken PyObjectDB.not.there.Atall instance
        b'\x00\x00\x00\x00\x00\x00\x00\x01'>

    >>> a3.__Broken_state__
    {'x': 1}

    Broken objects provide an interface:

    >>> from PyObjectDB.interfaces import IBroken
    >>> IBroken.providedBy(a3)
    True

    Let's clean up:

    >>> db.close()
    >>> del sys.modules['PyObjectDB.not']

    Cleanup:

    >>> import PyObjectDB.broken
    >>> PyObjectDB.broken.broken_cache.clear()
    """


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('PyObjectDB.broken', checker=checker),
        DocTestSuite(checker=checker),
    ))
