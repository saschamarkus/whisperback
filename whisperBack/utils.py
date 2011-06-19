#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send feedback in an encrypted mail
# Copyright (C) 2009-2011 Tails developers <amnesia.org>
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

"""various WhisperBack utility functions

"""

import os
import re
import urlparse
import locale

# Ugly pathes finder utilities

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

# Input validation fuctions

def is_valid_link(candidate):
  """Check if candidate seems to be a internet link
  
  @param candidate the URL to be checked

  @returns true if candidate is an URL with:
  - an hostname of the form domain.tld
  - a scheme http(s) or ftp(S)
  """
  parseresult = urlparse.urlparse(candidate)
  if (re.search(r'^(ht|f)tp(s)?$', parseresult.scheme) and
      re.search(r'^(\w{1,}\.){1,}\w{1,}$', parseresult.hostname)):
    return True
  else:
    return False

def is_valid_pgp_block(candidate):
  #pylint: disable=C0301
  if re.search(r"-----BEGIN PGP PUBLIC KEY BLOCK-----\n(?:.*\n)+-----END PGP PUBLIC KEY BLOCK-----",
        candidate):
    return True
  else:
    return False

def is_valid_pgp_id(candidate):
  #pylint: disable=C0301
  if re.search(r"(?:^(?:0x)?(?:[0-9a-fA-F]{8}){1,2}$)|(?:^(?:[0-9f-zA-F]{4} {0,2}){10}$)",
        candidate):
    return True
  else:
    return False

def is_valid_email(candidate):
  if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", candidate):
    return True
  else:
    return False

# Documentation localisation helpers

def get_wiki_supported_languages():
    try:
        return os.environ["TAILS_WIKI_SUPPORTED_LANGUAGES"].split(' ')
    except KeyError:
        return 'en'

def get_localised_documentation_language():
    # locale.getlocale returns a tuple (language code, encoding)
    # the language is the two first character of the RFC 1766 "language code"
    system_language = locale.getdefaultlocale()[0][0:2]

    if system_language in get_wiki_supported_languages():
        return system_language
    else:
        return 'en'

def get_localised_documentation_link():
    return ("file:///live/image/doc/amnesia/wiki/bug_reporting." +
        get_localised_documentation_language() +
        ".html")
