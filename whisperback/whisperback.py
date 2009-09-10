#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
LICENCE = """
WhisperBack - Send a feedback in an encrypted mail
Copyright (C) 2009 Amnesio <amnesia@boum.org>

This program is  free software; you can redistribute  it and/or modify
it under the  terms of the GNU General Public  License as published by
the Free Software Foundation; either  version 3 of the License, or (at
your option) any later version.

This program  is distributed in the  hope that it will  be useful, but
WITHOUT   ANY  WARRANTY;   without  even   the  implied   warranty  of
MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.   See  the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
########################################################################

VERSION = '0.0'
LOCALEDIR = "locale/"
PACKAGE = "whisperback"

########################################################################
#
# WhisperBack.py
#
# This file conatins...
#
########################################################################

# Import pygtk for the GUI
import pygtk
pygtk.require('2.0')
import gtk

# Import gettext for i18n
import gettext

# Import the required pyme modules
import pyme.core
import pyme.errors
#import pyme.core.Data
#import pyme.core.Context
#import pyme.constants.validity

# Import some configuration
import ConfigParser

# Import our modules
import mail

# Initialize gettext 
# FIXME : how to set these pathes ?
gettext.bindtextdomain(PACKAGE, LOCALEDIR)
gettext.textdomain(PACKAGE)
_ = gettext.gettext

class WhisperBackUI (object):
  """
  This class provides a window containing the GTK+ user interface.
  
  
  """

  def __init__(self, pdfconv = None):
    """Constructor of the class, which creates the main window
    
    This is where the main window will be created and filled with the 
    widgets we want.
    """

    builder = gtk.Builder()
    builder.add_from_file("data/whisperback.xml")
    builder.connect_signals(self)

    self.main_window = builder.get_object("windowMain")
    self.subject = builder.get_object("entrySubject")
    self.message = builder.get_object("textviewMessage")
    self.details = builder.get_object("labelDetails")
    self.send_button = builder.get_object("buttonSend")

    # Shows the UI
    self.main_window.show()

  # CALLBACKS

  def cb_close_application (self, widget, event, data=None):
    """Callback function for the main window's close event
    
    """
    self.close_application ()
    return False
  
  def cb_close_application (self, widget, data=None):
    """Callback function for the main window's close event
    
    """
    self.close_application ()
    return False
  
  def cb_show_about (self, widget, data=None):
    """Callback function to show the "about" dialog
    
    """
    self.show_about_dialog ()
    return False
    
  def cb_send_message (self, widget, data=None):
    """Callback function to actually send the message
    
    """
    
    self.main_window.set_sensitive(False)
    
    try:
      WhisperBack (self.subject.get_text(), 
                   self.message.get_buffer().get_text(
                                self.message.get_buffer().get_start_iter(),
                                self.message.get_buffer().get_end_iter()),
                   self.details.get_text()).send()
    except EncryptionException, e:
      self.show_exception_dialog (_("An error occured during encryption."), e)
      return False
    except KeyNotFoundException, e:
      self.show_exception_dialog (_("Unable to find encryption key."), e)
      return False
    
    dialog = gtk.MessageDialog (parent=self.main_window, 
                       flags=gtk.DIALOG_MODAL,
                       type=gtk.MESSAGE_INFO,
                       buttons=gtk.BUTTONS_CLOSE,
                       message_format=_("Your message has been sent.")
                       )
    dialog.connect("response", self.cb_close_application)
    dialog.show()
    
    return False
    
  def show_exception_dialog(self, message, exception):
    """Shows a dialog reporting an exception
    
    @param message A string explaining the exception
    @param exception The exception
    """
    dialog = gtk.MessageDialog (parent=self.main_window, 
                       flags=gtk.DIALOG_MODAL,
                       type=gtk.MESSAGE_ERROR,
                       buttons=gtk.BUTTONS_CLOSE)
    dialog.set_markup ("<b>%s</b>\n\n%s\n" % (message, exception.message()))
    dialog.connect("response", self.cb_close_exception_dialog)
    dialog.show()
    
  def cb_close_exception_dialog (self, widget, data=None):
    """Callback function for the exception dialog close event
    
    """
    self.main_window.set_sensitive(True)
    widget.hide()
    return False

  def show_about_dialog(self):
    """Shows an "about" dialog for the program
    
    """
        
    # Creates the about dialog
    about_dialog = gtk.AboutDialog()
    about_dialog.set_transient_for(self.main_window)
    about_dialog.set_version(VERSION)
    about_dialog.set_name(_("WhisperBack"))
    about_dialog.set_comments(_("Send a feedback in an encrypted mail."))
    about_dialog.set_license(LICENCE)
    about_dialog.set_copyright(_("Copyright © 2009 amnesia@boum.org"))
    about_dialog.set_authors(["Amnesia team <amnesia@boum.org>"])
    about_dialog.set_translator_credits (_("translator-credits"))
    about_dialog.set_website("https://amnesia.boum.org")
    about_dialog.connect("response", gtk.Widget.hide_on_delete)
    about_dialog.show()

  def close_application (self):
    """
    Closes the application
    
    """
    gtk.main_quit()

########################################################################

class Encryption (object):
  """Some tools for encryption"""
  
  def __init__ (self):
    """Initialize the encryption mechanism"""
    
    # Some true initialisation : create a pyme context
    self.context = pyme.core.Context()
    
  def __fingerprints_to_keys (self, fingerprints):
    """Convert fingerprints into pyme keys
    
    @param fingerprints A list of fingerprints
    
    @return A list of pygme keys
    """
    
    # Set up the recipients.
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


class WhisperBack (object):
  """
  This class contains the backend which actually sends the feedback
  """
  
  def __init__ (self, subject, message, details):
    """Initialize a feedback object with the given contents
    
    @param subject The topic of the feedback 
    @param message The content of the feedback
    @param details The details of the used software
    """
    
    # Load the configuration
    self.__load_conf ('whisperback.conf')
    
    # Initialize variables
    self.subject = subject
    self.message = message
    self.details = details
    
  
  def __load_conf (self, config_file_path):
    """Loads a configuration file from config_file_path and initialize
    the corresponding instance variables.
    
    @param config_file_path The path on the configuration file to load
    """
        
    config = ConfigParser.SafeConfigParser()
    config.read(config_file_path)

    self.to_address = config.get('dest', 'address')
    self.to_fingerprint = config.get('dest', 'fingerprint')
    
    self.from_address = config.get('sender', 'address')
    
    self.mail_subject = config.get('message', 'subject')
    
    self.smtp_host = config.get('smtp', 'host')
    self.smtp_port = config.get('smtp', 'port')
      
  
  def send(self):
    """Actually sends the message"""
    
    message_body = "Subject: " + self.subject + "\n" + \
                   "Details: " + self.details + "\n\n" + \
                   self.message + "\n"
    
    encrypted_message_body = Encryption().encrypt(message_body, 
                                                  [self.to_fingerprint])
    
    mail.create_message (self.from_address, self.to_address, 
                         self.mail_subject, encrypted_message_body)
    
    mail.send_message (self.from_address, self.to_address, 
                       encrypted_message_body, self.smtp_host,
                       self.smtp_port)
    
    
class KeyNotFoundException (Exception):
  """This exception is raised when GPGME can't find the key it searches 
  in the keyring"""
  pass

class EncryptionException (Exception):
  """This exception is raised when GPGME fails to encrypt the data"""
  pass

########################################################################
  
def main():
  """
  This is the function that launches the program
  """
    
  ui = WhisperBackUI()
  gtk.main()
  
  return 0 
  
if __name__ == "__main__":
  main()
