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

# Import smtplib for the actual sending function
import smtplib
# Import the email modules we'll need
from email.mime.text import MIMEText

# Import the required pyme modules
import pyme.core
import pyme.core.Data
import pyme.core.Context
#import pyme.constants.validity

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

    WhisperBack (self.subject.get_text(), 
                 self.message.get_buffer().get_text(
                              self.message.get_buffer().get_start_iter(), 
                              self.message.get_buffer().get_end_iter()),
                 self.details.get_text())
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
    about_dialog.set_authors(["Amnesia team <amnesia@boum.org"])
    about_dialog.set_translator_credits (_("translator-credits"))
    about_dialog.set_website("http://amnesia.boum.org")
    about_dialog.connect("response", gtk.Widget.hide_on_delete)
    about_dialog.show()

  def close_application (self):
    """
    Closes the application
    
    """
    gtk.main_quit()

########################################################################


class WhisperBack ():
  """
  This class contains the backend which actually sends the feedback
  """
  
  def __init__ (self, subject, message, details):
    """Sends a feedback with the given contents
    
    @param subject The topic of the feedback 
    @param message The content of the feedback
    @param details The details of the used software
    """
    
    # Some true initialisation : create a pyme context
    self.context = pyme.core.Context()
    
    print ("should send a message")
    print ("subject: " + subject)
    print ("message: " + message)
    print ("details: " + details)

  def __fingerprints_to_keys (self, fingerprints):
    """Convert fingerprints into pyme keys
    
    @param fingerprints A list of fingerprints
    
    @return A list of pygme keys
    """
    
    # Set up the recipients.
    to_keys = []
    
    for to_fingerprint in to_fingerprints:
      try:
        # The function gpgme_op_keylist_start initiates a key listing
        # operation inside the context ctx. It sets everything up so that
        # subsequent invocations of gpgme_op_keylist_next return the keys
        # in the list.
        to_key = self.context.get_key(to_fingerprint, secret=False)

        to_keys.append (to_key)
      except GPGMEError, e:
        print e.getstring()
    
    return to_keys
    
  def __encrypt_from_keys (data, to_keys):
    """Encrypt data to a list of keys 
    
    @param to_keys  A list of pyme keys, as returned by 
                    __fingerprint_to_keys
    @param data The data to be encrypted
    
    @return The encrypted data
    
    """
    
    # Do the actual encryption.
    try:
      # Do the actual encryption 
      
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
      #
      # FIXME: why do we use GPGME_ENCRYPT_ALWAYS_TRUST?
      context.op_encrypt([recepient], 1, plain, cipher)
      
      # Reads the cipher (= encrypted text) from the beginning to the
      # end
      # FIXME: why to do this?
      cipher.seek(0,0)
      
      # Returns the cipher (= encrypted text)
      return cipher.read()
      
    except errors.GPGMEError, ex:
      print ex.getstring()
      raise ex


  def __encrypt (data, to_fingerprints):
    """Encrypts data for a list of recepients
    
    This is from an example of the pyme package distribution
    
    @param to_fingerprints A list of recepient's key fingerprints
    @param data Data to be encrypted
    
    @return The encrypted data
    """
  
    # THE BUFFERS
  
    # Set up our input buffer and initialize it whit our message
    plain = pyme.core.Data(data)
    # Set up our output buffer
    cipher = pyme.core.Data()

    # THE CONTEXT
    
    # Initialize our context
    context = self.context
    
    # Define which protocol we want to use 
    #context.set_protocol(PROTOCOL)
     
    # Define that we want an ASCII-armored output
    context.set_armor(True)
    
    # KEYS
    
    # Convert fingerprint into pgpme keys
    to_keys = __fingerprints_to_keys (to_fingerprints)
    
    # Process only if some keys were found
    if (to_keys.length == 0):
      raise Exception ( _("no key found") )
      return
    
    # ENCRYPT
    
    
  def __find_fingerprint (to_addresse):
    """Gets the fingerprints from a recepient address
    
    @param to_addresse A recepient's addresse
    
    @return A list of the fingerprint found, if any
    """
    
    recepient_keys = []
    
    # The function gpgme_op_keylist_start initiates a key listing
    # operation inside the context ctx. It sets everything up so that
    # subsequent invocations of gpgme_op_keylist_next return the keys
    # in the list.
    context.op_keylist_start(to_address, 0)
    
    while True:
      try:
        # op_keylist_next eturns the next key in the list created by a 
        # previous op_keylist_start operation in the context and append it
        recepient_key = context.op_keylist_next()
        
        # Next we append it to our recipient_keys list
        recepient_keys.append (recepient_key)
        
      except GPGMEError, e:
        print e.getstring()
        break
      
      finally:
        return recepient_keys
      
  def __create_message (from_address, to_address, subject, message):
    """Actually create a plaintext mail
    
    This is from an example from doc.python.org
    
    @param from_address The sender's address
    @param to_address The recipient address
    @param subject The topic
    @param message The content of the text message
    
    @return the message to send
    """
  
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    
    return msg.as_string()

  def __sendmail (from_address, to_address, message)
    """Actually sends a mail
    
    This is from an example from doc.python.org
    
    @param from_address The sender's address
    @param to_address The recipient address
    @param message The content of the mail
    """
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    smtp = smtplib.SMTP()
    smtp.sendmail(from_address, [to_address], )
    smtp.quit()


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
