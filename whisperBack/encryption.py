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
import email.encoders
import email.mime.application
import email.mime.base
import email.mime.multipart
import email.mime.text
import gnupg
import os.path

import whisperBack.exceptions

class Encryption ():
    """Some tools for encryption"""

    def __init__ (self, keyring=None):
        """Initialize the encryption mechanism"""

        if not (keyring and os.path.exists(keyring)):
            keyring = None

        self._gpg = gnupg.GPG(keyring=keyring)

    # XXX: credits
    def pgp_mime_encrypt(self, message, to_fingerprints):
        """Encrypts  for a list of recepients
        
        @param to_fingerprints A list of recepient's key fingerprints
        @param message MIME message to be encrypted. 
        @return The encrypted data
        """
        assert isinstance(message, email.mime.base.MIMEBase)

        encrypted_content = self._gpg.encrypt(message.as_string(), to_fingerprints, always_trust=True)
        if not encrypted_content:
            # XXX: raise a specific exception if the key wasn't found
            raise whisperBack.exceptions.EncryptionException(crypt.status)

        enc = email.mime.application.MIMEApplication(
                _data=str(encrypted_content),
                _subtype='octet-stream; name="encrypted.asc"',
                _encoder=email.encoders.encode_7or8bit)
        enc['Content-Description'] = 'OpenPGP encrypted message'
        enc.set_charset('us-ascii')

        control = email.mime.application.MIMEApplication(
                _data='Version: 1\n',
                _subtype='pgp-encrypted',
                _encoder=email.encoders.encode_7or8bit)
        control.set_charset('us-ascii')

        encmsg = email.mime.multipart.MIMEMultipart(
                'encrypted',
                protocol='application/pgp-encrypted')
        encmsg.attach(control)
        encmsg.attach(enc)
        encmsg['Content-Disposition'] = 'inline'

        return encmsg
