#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send feedback in an encrypted mail
# Copyright (C) 2009-2012 Tails developers <amnesia.org>
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

"""Some tools for encryption

"""
import os.path

import GnuPGInterface

import whisperBack.exceptions

class Encryption (GnuPGInterface.GnuPG):
    """Some tools for encryption"""
    
    def __init__ (self, gnupg_homedir=None):
        """Initialize the encryption mechanism"""

        GnuPGInterface.GnuPG.__init__(self)

        self.options.armor = True
        self.options.meta_interactive = False
        self.options.always_trust = True

        if gnupg_homedir and os.path.exists(gnupg_homedir):
            self.options.homedir = gnupg_homedir
 
    def encrypt (self, data, to_fingerprints):
        """Encrypts data for a list of recepients
        
        @param to_fingerprints A list of recepient's key fingerprints
        @param data Data to be encrypted
        @return The encrypted data
        """
        try:
            self.options.recipients = to_fingerprints
            proc = self.run(['--encrypt'], create_fhs=['stdin', 'stdout', 'stderr'])

            proc.handles['stdin'].write(data)
            proc.handles['stdin'].close()

            output = proc.handles['stdout'].read()
            proc.handles['stdout'].close()

            error = proc.handles['stderr'].read()
            proc.handles['stderr'].close()

            proc.wait()
            return output

        except IOError, e:
            # XXX: raise a specific exception if the key wasn't found
            raise whisperBack.exceptions.EncryptionException(error)
