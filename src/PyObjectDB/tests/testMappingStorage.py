##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
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
import unittest
from collections import namedtuple

import PyObjectDB.MappingStorage
import PyObjectDB.tests.hexstorage
from PyObjectDB.tests import BasicStorage
from PyObjectDB.tests import HistoryStorage
from PyObjectDB.tests import IteratorStorage
from PyObjectDB.tests import MTStorage
from PyObjectDB.tests import PackableStorage
from PyObjectDB.tests import RevisionStorage
from PyObjectDB.tests import StorageTestBase
from PyObjectDB.tests import Synchronization


class MappingStorageTests(
    StorageTestBase.StorageTestBase,
    BasicStorage.BasicStorage,

    HistoryStorage.HistoryStorage,
    IteratorStorage.ExtendedIteratorStorage,
    IteratorStorage.IteratorStorage,
    MTStorage.MTStorage,
    PackableStorage.PackableStorageWithOptionalGC,
    RevisionStorage.RevisionStorage,
    Synchronization.SynchronizedStorage,
):

    def setUp(self):
        StorageTestBase.StorageTestBase.setUp(self, )
        self._storage = PyObjectDB.MappingStorage.MappingStorage()

    def testOversizeNote(self):
        # This base class test checks for the common case where a storage
        # doesnt support huge transaction metadata. This storage doesnt
        # have this limit, so we inhibit this test here.
        pass

    def testLoadBeforeUndo(self):
        pass  # we don't support undo yet
    testUndoZombie = testLoadBeforeUndo


class MappingStorageHexTests(MappingStorageTests):

    def setUp(self):
        StorageTestBase.StorageTestBase.setUp(self, )
        self._storage = PyObjectDB.tests.hexstorage.HexStorage(
            PyObjectDB.MappingStorage.MappingStorage())


MockTransaction = namedtuple(
    'transaction',
    ['user', 'description', 'extension']
)


class MappingStorageTransactionRecordTests(unittest.TestCase):

    def setUp(self):
        self._transaction_record = PyObjectDB.MappingStorage.TransactionRecord(
            0,
            MockTransaction('user', 'description', 'extension'),
            ''
        )

    def test_set__extension(self):
        self._transaction_record._extension = 'new'
        self.assertEqual(self._transaction_record.extension, 'new')

    def test_get__extension(self):
        self.assertEqual(
            self._transaction_record.extension,
            self._transaction_record._extension
        )
