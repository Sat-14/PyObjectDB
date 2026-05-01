import threading
import time

import PyObjectDB


class PyObjectDBClientThread(threading.Thread):

    sleep_time = 3

    def __init__(self, db, test):
        threading.Thread.__init__(self)
        self._exc_info = None
        self.daemon = True
        self.db = db
        self.test = test
        self.event = threading.Event()

    def run(self):
        conn = self.db.open()
        conn.sync()
        self.event.set()
        time.sleep(self.sleep_time)

        # conn.close calls self.transaction_manager.unregisterSynch(self)
        # and this succeeds.
        conn.close()


class ShutdownTest(PyObjectDB.tests.util.TestCase):

    def setUp(self):
        # Our default transaction manager is
        # transaction._manager.ThreadTransactionManager
        # so no need to set it.
        PyObjectDB.tests.util.TestCase.setUp(self)
        self._storage = PyObjectDB.FileStorage.FileStorage(
            'PyObjectDBTests.fs', create=1)
        self._db = PyObjectDB.DB(self._storage)

    def tearDown(self):
        PyObjectDB.tests.util.TestCase.tearDown(self)

    def test_shutdown(self):
        client_thread = PyObjectDBClientThread(self._db, self)
        client_thread.start()
        client_thread.event.wait()
        # calls conn._release_resources, that calls conn.close(),
        # that calls conn.transaction_manager.unregisterSynch(self),
        # but from a different thread, so transaction_manager._synchs
        # have different contents.
        self._db.close()

        # Be sure not to 'leak' the running thread; if it hasn't
        # finished after this, something went very wrong
        client_thread.join(client_thread.sleep_time + 10)
        if client_thread.is_alive():
            self.fail("Client thread failed to close connection")
