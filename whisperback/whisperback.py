#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
LICENCE = """
WhisperBack - Send a feedback in an encrypted mail
Copyright (C) 2009 Amnesia <amnesia@boum.org>

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

VERSION = '0.1'
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

# Import some configuration
import ConfigParser

# Import our modules
import mail
import encryption

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
    
    # Retrives info on the system
    self.details.set_text(SystemInformations().get_info())


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
    except encryption.EncryptionException, e:
      self.show_exception_dialog (_("An error occured during encryption."), e)
      return False
    except encryption.KeyNotFoundException, e:
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
    
    encrypted_message_body = encryption.Encryption(). \
                             encrypt(message_body, [self.to_fingerprint])
    
    mail.create_message (self.from_address, self.to_address, 
                         self.mail_subject, encrypted_message_body)
    
    mail.send_message (self.from_address, self.to_address, 
                       encrypted_message_body, self.smtp_host,
                       self.smtp_port)

########################################################################

class SystemInformations (object):
  """Retrives informations on the running system
  
  """
  
  def get_info (self):
    """Returns a summary of the informations on the running system
    
    @return a summary of the informations on the running system
    """
    
    return "This is a test"

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
