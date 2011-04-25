#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send feedback in an encrypted mail
# Copyright (C) 2009-2010 Tails developers <amnesia.org>
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
# encryption.py
#
# Some tools for encryption
#
########################################################################

import pyme.core
import pyme.errors

import exceptions

class Encryption (object):
  """Some tools for encryption"""
  
  def __init__ (self):
    """Initialize the encryption mechanism"""

    self.context = pyme.core.Context()
    
  def __fingerprints_to_keys (self, fingerprints):
    """Convert fingerprints into pyme keys
    
    @param fingerprints A list of fingerprints
    @return A list of pygme keys
    """

    to_keys = []
    for fingerprint in fingerprints:
      try:
        # The function gpgme_op_keylist_start initiates a key listing
        # operation inside the context ctx. It sets everything up so that
        # subsequent invocations of gpgme_op_keylist_next return the keys
        # in the list.
        to_key = self.context.get_key(fingerprint, secret=False)
        to_keys.append (to_key)
      except pyme.errors.GPGMEError, e:
        raise KeyNotFoundException (e.getstring)
    return to_keys
    
  def __encrypt_from_keys (self, data, to_keys):
    """Encrypt data to a list of keys 
    
    @param to_keys  A list of pyme keys, as returned by 
                    __fingerprint_to_keys
    @param data The data to be encrypted
    @return The encrypted data
    """
    
    # THE CONTEXT
    # Initialize our context
    context = self.context
    # Define which protocol we want to use 
    #context.set_protocol(PROTOCOL)
    # Define that we want an ASCII-armored output
    context.set_armor(True)
    
    # THE BUFFERS
    # Set up our input buffer and initialize it whit our message
    plain = pyme.core.Data(data)
    # Set up our output buffer
    cipher = pyme.core.Data()
    
    # THE ACTUAL ENCRYPTION
    # Do the actual encryption.
    try:
      # Do the actual encryption 
      #
      # The function gpgme_op_encrypt encrypts the plaintext in the data
      # object plain for the recipients recp and stores the ciphertext 
      # in the data object cipher. The type of the ciphertext created is
      # determined by the ASCII armor and text mode attributes set for
      # the context.
      #
      # Key must be a NULL-terminated array of keys. The user must keep
      # references for all keys during the whole duration of the call
      # (but see gpgme_op_encrypt_start for the requirements with the
      # asynchronous variant). 
      #
      # flags := {GPGME_ENCRYPT_ALWAYS_TRUST : 1, 
      #           GPGME_ENCRYPT_NO_ENCRYPT_TO : 2}
      #
      # context.op_encrypt (keys[], flags, plain, cipher)
      context.op_encrypt(to_keys, 1, plain, cipher)
      del plain
      # Go to the beginning of the buffer
      cipher.seek(0,0)
      # Reads the cipher (= encrypted text)
      return cipher.read()
    except pyme.errors.GPGMEError, e:
      raise EncryptionException (e.getstring())

  def encrypt (self, data, to_fingerprints):
    """Encrypts data for a list of recepients
    
    @param to_fingerprints A list of recepient's key fingerprints
    @param data Data to be encrypted
    @return The encrypted data
    """
    
    # Convert the fingerprint into pgpme keys
    to_keys = self.__fingerprints_to_keys (to_fingerprints)
    # Process only if some keys were found
    if len(to_keys) == 0:
      raise KeyNotFoundException ( _("No keys found.") )
    # Encrypt the data
    return self.__encrypt_from_keys (data, to_keys)
