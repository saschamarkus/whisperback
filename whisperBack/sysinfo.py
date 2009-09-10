#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send a feedback in an encrypted mail
# Copyright (C) 2009 Amnesio <amnesia@boum.org>
# 
# This program is  free software; you can redistribute  it and/or modify
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
# sysinfo.py
#
# Retrives informations on the running system
#
########################################################################

import subprocess

class SystemInformations (object):
  """Retrives informations on the running system
  
  """
  
  def get_info (self):
    """Returns a summary of the informations on the running system
    
    @return a summary of the informations on the running system
    """
    
    return None

########################################################################

class AmnesiaSystemInformations (SystemInformations):
  """Retrives informations on the running amnesia system
  
  """
  
  def get_info (self):
    """Returns a summary of the informations on the running amnesia system
    
    @return The output of amnesia-version, if any, or an english string 
            explaining the error
    """
  
    try:
      amnesia_version = subprocess.Popen ("amnesia-version", 
                                          stdout=subprocess.PIPE)
      amnesia_version.wait()
      system_information = "Amnesia-Version: %s\n" % \
                           amnesia_version.stdout.read()
    except OSError, e:
      system_information = "amnesia-version command not found"
    except subprocess.CalledProcessError, e:
      system_information = "amnesia-version returned an error"
    
    return system_information
