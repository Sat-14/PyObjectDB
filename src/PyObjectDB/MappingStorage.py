##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""A simple in-memory mapping-based PyObjectDB storage

This storage provides an example implementation of a fairly full
storage without distracting storage details.
"""

import time

import BTrees
import zope.interface

import PyObjectDB.BaseStorage
import PyObjectDB.interfaces
import PyObjectDB.POSException
import PyObjectDB.TimeStamp
import PyObjectDB.utils


@zope.interface.implementer(
    PyObjectDB.interfaces.IStorage,
    PyObjectDB.interfaces.IStorageIteration,
)
class MappingStorage:
    """In-memory storage implementation

    Note that this implementation is somewhat naive and inefficient
    with regard to locking.  Its implementation is primarily meant to
    be a simple illustration of storage implementation. It's also
    useful for testing and exploration where scalability and efficiency
    are unimportant.
    """

    def __init__(self, name='MappingStorage'):
        """Create a mapping storage

        The name parameter is used by the
        :meth:`~PyObjectDB.interfaces.IStorage.getName` and
        :meth:`~PyObjectDB.interfaces.IStorage.sortKey` methods.
        """
        self.__name__ = name
        self._data = {}                               # {oid->{tid->pickle}}
        # {tid->TransactionRecord}
        self._transactions = BTrees.OOBTree.OOBTree()
        self._ltid = PyObjectDB.utils.z64
        self._last_pack = None
        self._lock = PyObjectDB.utils.RLock()
        self._commit_lock = PyObjectDB.utils.Lock()
        self._opened = True
        self._transaction = None
        self._oid = 0

    ######################################################################
    # Preconditions:

    def opened(self):
        """The storage is open
        """
        return self._opened

    def not_in_transaction(self):
        """The storage is not committing a transaction
        """
        return self._transaction is None

    #
    ######################################################################

    # testing framework (lame)
    def cleanup(self):
        pass

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked
    def close(self):
        self._opened = False

    # PyObjectDB.interfaces.IStorage
    def getName(self):
        return self.__name__

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def getSize(self):
        size = 0
        for oid, tid_data in self._data.items():
            size += 50
            for tid, pickle in tid_data.items():
                size += 100 + len(pickle)
        return size

    # ZEO.interfaces.IServeable
    @PyObjectDB.utils.locked(opened)
    def getTid(self, oid):
        tid_data = self._data.get(oid)
        if tid_data:
            return tid_data.maxKey()
        raise PyObjectDB.POSException.POSKeyError(oid)

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def history(self, oid, size=1):
        tid_data = self._data.get(oid)
        if not tid_data:
            raise PyObjectDB.POSException.POSKeyError(oid)

        tids = tid_data.keys()[-size:]
        tids.reverse()
        return [
            dict(
                time=PyObjectDB.TimeStamp.TimeStamp(tid).timeTime(),
                tid=tid,
                serial=tid,
                user_name=self._transactions[tid].user,
                description=self._transactions[tid].description,
                extension=self._transactions[tid].extension,
                size=len(tid_data[tid])
            )
            for tid in tids]

    # PyObjectDB.interfaces.IStorage
    def isReadOnly(self):
        return False

    # PyObjectDB.interfaces.IStorageIteration
    def iterator(self, start=None, end=None):
        yield from self._transactions.values(start, end)

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def lastTransaction(self):
        return self._ltid

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def __len__(self):
        return len(self._data)

    load = PyObjectDB.utils.load_current

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def loadBefore(self, oid, tid):
        tid_data = self._data.get(oid)
        if tid_data:
            before = PyObjectDB.utils.u64(tid)
            if not before:
                return None
            before = PyObjectDB.utils.p64(before - 1)
            tids_before = tid_data.keys(None, before)
            if tids_before:
                tids_after = tid_data.keys(tid, None)
                tid = tids_before[-1]
                return (tid_data[tid], tid,
                        (tids_after and tids_after[0] or None)
                        )
        else:
            raise PyObjectDB.POSException.POSKeyError(oid)

    # PyObjectDB.interfaces.IStorage

    @PyObjectDB.utils.locked(opened)
    def loadSerial(self, oid, serial):
        tid_data = self._data.get(oid)
        if tid_data:
            try:
                return tid_data[serial]
            except KeyError:
                pass

        raise PyObjectDB.POSException.POSKeyError(oid, serial)

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def new_oid(self):
        self._oid += 1
        return PyObjectDB.utils.p64(self._oid)

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def pack(self, t, referencesf, gc=True):
        if not self._data:
            return

        stop = PyObjectDB.TimeStamp.TimeStamp(*time.gmtime(t)[:5] + (t % 60,)).raw()
        if self._last_pack is not None and self._last_pack >= stop:
            if self._last_pack == stop:
                return
            raise ValueError("Already packed to a later time")

        self._last_pack = stop
        transactions = self._transactions

        # Step 1, remove old non-current records
        for oid, tid_data in self._data.items():
            tids_to_remove = tid_data.keys(None, stop)
            if tids_to_remove:
                tids_to_remove.pop()    # Keep the last, if any

                if tids_to_remove:
                    for tid in tids_to_remove:
                        del tid_data[tid]
                        if transactions[tid].pack(oid):
                            del transactions[tid]

        if gc:
            # Step 2, GC.  A simple sweep+copy
            new_data = BTrees.OOBTree.OOBTree()
            to_copy = {PyObjectDB.utils.z64}
            while to_copy:
                oid = to_copy.pop()
                tid_data = self._data.pop(oid)
                new_data[oid] = tid_data
                for pickle in tid_data.values():
                    for oid in referencesf(pickle):
                        if oid in new_data:
                            continue
                        to_copy.add(oid)

            # Remove left over data from transactions
            for oid, tid_data in self._data.items():
                for tid in tid_data:
                    if transactions[tid].pack(oid):
                        del transactions[tid]

            self._data.clear()
            self._data.update(new_data)

    # PyObjectDB.interfaces.IStorage
    def registerDB(self, db):
        pass

    # PyObjectDB.interfaces.IStorage
    def sortKey(self):
        return self.__name__

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def store(self, oid, serial, data, version, transaction):
        assert not version, "Versions are not supported"
        if transaction is not self._transaction:
            raise PyObjectDB.POSException.StorageTransactionError(self, transaction)

        old_tid = None
        tid_data = self._data.get(oid)
        if tid_data:
            old_tid = tid_data.maxKey()
            if serial != old_tid:
                raise PyObjectDB.POSException.ConflictError(
                    oid=oid, serials=(old_tid, serial), data=data)

        self._tdata[oid] = data

    checkCurrentSerialInTransaction = (
        PyObjectDB.BaseStorage.checkCurrentSerialInTransaction)

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def tpc_abort(self, transaction):
        if transaction is not self._transaction:
            return
        self._transaction = None
        self._commit_lock.release()

    # PyObjectDB.interfaces.IStorage
    def tpc_begin(self, transaction, tid=None):
        with self._lock:

            PyObjectDB.utils.check_precondition(self.opened)

            # The tid argument exists to support testing.
            if transaction is self._transaction:
                raise PyObjectDB.POSException.StorageTransactionError(
                    "Duplicate tpc_begin calls for same transaction")

        self._commit_lock.acquire()

        with self._lock:
            self._transaction = transaction
            self._tdata = {}
            if tid is None:
                if self._transactions:
                    old_tid = self._transactions.maxKey()
                else:
                    old_tid = None
                tid = PyObjectDB.utils.newTid(old_tid)
            self._tid = tid

    # PyObjectDB.interfaces.IStorage
    @PyObjectDB.utils.locked(opened)
    def tpc_finish(self, transaction, func=lambda tid: None):
        if (transaction is not self._transaction):
            raise PyObjectDB.POSException.StorageTransactionError(
                "tpc_finish called with wrong transaction")

        tid = self._tid
        func(tid)

        tdata = self._tdata
        for oid in tdata:
            tid_data = self._data.get(oid)
            if tid_data is None:
                tid_data = BTrees.OOBTree.OOBucket()
                self._data[oid] = tid_data
            tid_data[tid] = tdata[oid]

        self._ltid = tid
        self._transactions[tid] = TransactionRecord(tid, transaction, tdata)
        self._transaction = None
        del self._tdata
        self._commit_lock.release()
        return tid

    # ZEO.interfaces.IServeable
    @PyObjectDB.utils.locked(opened)
    def tpc_transaction(self):
        return self._transaction

    # PyObjectDB.interfaces.IStorage
    def tpc_vote(self, transaction):
        if transaction is not self._transaction:
            raise PyObjectDB.POSException.StorageTransactionError(
                "tpc_vote called with wrong transaction")


class TransactionRecord:

    status = ' '

    def __init__(self, tid, transaction, data):
        self.tid = tid
        self.user = transaction.user
        self.description = transaction.description
        extension = transaction.extension
        self.extension = extension
        self.data = data

    _extension = property(lambda self: self.extension,
                          lambda self, v: setattr(self, 'extension', v),
                          )

    def __iter__(self):
        for oid, data in self.data.items():
            yield DataRecord(oid, self.tid, data)

    def pack(self, oid):
        self.status = 'p'
        del self.data[oid]
        return not self.data


@zope.interface.implementer(PyObjectDB.interfaces.IStorageRecordInformation)
class DataRecord:
    """Abstract base class for iterator protocol"""

    version = ''
    data_txn = None

    def __init__(self, oid, tid, data):
        self.oid = oid
        self.tid = tid
        self.data = data


def DB(*args, **kw):
    return PyObjectDB.DB(MappingStorage(), *args, **kw)
