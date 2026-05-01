==================
PyObjectDB documentation
==================

``PyObjectDBdocs`` is the source documentation for the website https://PyObjectDB.readthedocs.io. It
contains all PyObjectDB relevant documentation like "PyObjectDB/ZEO Programming Guide",
some PyObjectDB articles and links to the PyObjectDB release notes.


Building the documentation
--------------------------

All documentation is formatted as restructured text. To generate HTML using
Sphinx, use the following::

    python bootstrap.py
    ./bin/buildout
    make html
