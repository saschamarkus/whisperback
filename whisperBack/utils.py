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
# utils.py
#
# Ugly pathes finder utility
#
########################################################################

import os

def guess_prefix ():
  """Tries to guess the prefix
  
  @return The guessed prefix"""

  # XXX: hardcoded path !
  if os.path.exists ("/usr/local/share/whisperback"):
    return "/usr/local"
  elif os.path.exists ("/usr/share/whisperback"):
    return "/usr"
  else:
    return None

def get_sharedir ():
  """Tries to guess the shared data directiry
  
  @return The guessed shared data directiry"""

  if guess_prefix():
    return os.path.join (guess_prefix(), "share")
  else:
    return "data"

def get_datadir ():
  """Tries to guess the datadir
  
  @return The guessed datadir"""
  if guess_prefix():
    return os.path.join (get_sharedir(), "whisperback")
  else:
    return "data"

def get_pixmapdir ():
  """Tries to guess the pixmapdir
  
  @return The guessed pixmapdir"""

  if guess_prefix():
    return os.path.join (get_sharedir(), "pixmaps")
  else:
    return "data"
