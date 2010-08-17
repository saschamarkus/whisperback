#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send a feedback in an encrypted mail
# Copyright (C) 2009-2010 Amnesia <amnesia@boum.org>
#
# This file is part of WhisperBack
#
# WhisperBack is  free software; you can redistribute  it and/or modify
# it under the  terms of the GNU General Public  License as published by
# the Free Software Foundation; either  version 3 of the License, or (at
# your option) any later version.
# 
# This program  is distributed in the  hope that it will  be useful, but
# WITHOUT   ANY  WARRANTY;   without  even   the  implied   warranty  of
# MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.   See  the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
########################################################################

########################################################################
# 
# exceptions.py
#
# Base exceptions for whisperback
#
########################################################################

class WhisperbackException(Exception):
    """Base class for all exceptions raised by WhisperBack"""
    pass

# Used in whisperback.py

class MisconfigurationException(WhisperbackException):
  """This exception is raised when the configuartion can't be properly
  loaded

  """
  def __init__(self, variable):
    WhisperbackException.__init__(self, _("The variable %s was not found in any of the configuation files /etc/whisperback/config.py, ~/.whisperback/config.py, ./config.py") % variable)

# Used in encryption.py

class EncryptionException (WhisperbackException):
  """This exception is raised when GPGME fails to encrypt the data"""
  pass

class KeyNotFoundException (EncryptionException):
  """This exception is raised when GPGME can't find the key it searches 
  in the keyring"""
  pass