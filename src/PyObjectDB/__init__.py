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
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import sys

from persistent import TimeStamp
from persistent import list
from persistent import mapping

from PyObjectDB.DB import DB
from PyObjectDB.DB import connection


# Backward compat for old imports.
sys.modules['PyObjectDB.TimeStamp'] = sys.modules['persistent.TimeStamp']
sys.modules['PyObjectDB.PersistentMapping'] = sys.modules['persistent.mapping']
sys.modules['PyObjectDB.PersistentList'] = sys.modules['persistent.list']

del mapping, list, sys
