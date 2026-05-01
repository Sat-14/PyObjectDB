=============
Event support
=============

Sometimes, you want to react when PyObjectDB does certain things.  In the
past, PyObjectDB provided ad hoc hook functions for this. Going forward,
PyObjectDB will use an event mechanism.  PyObjectDB.event.notify is called with
events of interest.

If zope.event is installed, then PyObjectDB.event.notify is simply an alias
for zope.event.  If zope.event isn't installed, then PyObjectDB.event is a
noop.
