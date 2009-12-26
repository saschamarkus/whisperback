#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
__licence__ = """
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

__version__ = '1.1-beta2'
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
import gobject

# Import gettext for i18n
#import gettext

# Import os services
import os

# Used to by show_exception_dialog to print exception traceback
import traceback

# Import our modules
import mail
import encryption
import utils

# Import smtplib because we need the exception it raises
import smtplib

# Initialize gettext 
# FIXME : how to set these pathes ?
#gettext.bindtextdomain(PACKAGE, LOCALEDIR)
#gettext.textdomain(PACKAGE)
#_ = gettext.gettext

class WhisperBackUI(object):
  """
  This class provides a window containing the GTK+ user interface.
  
  """

  def __init__(self):
    """Constructor of the class, which creates the main window
    
    This is where the main window will be created and filled with the 
    widgets we want.
    """

    builder = gtk.Builder()
    builder.add_from_file(os.path.join(utils.get_datadir(),
                                      "whisperback.xml"))
    builder.connect_signals(self)

    self.main_window = builder.get_object("windowMain")
    self.subject = builder.get_object("entrySubject")
    self.message = builder.get_object("textviewMessage")
    self.prepended_details = builder.get_object("textviewPrependedInfo")
    self.appened_details = builder.get_object("textviewAppenedInfo")
    self.send_button = builder.get_object("buttonSend")

    try:
      self.main_window.set_icon_from_file(os.path.join(
          utils.get_pixmapdir(), "whisperback.svg"))
    except gobject.GError, e:
      print e

    # Shows the UI
    self.main_window.show()

    # Launches the backend
    try:
      self.backend = WhisperBack()
    except MisconfigurationException, e:
      self.show_exception_dialog(_("Unable to load a valid configuration."), e, self.cb_close_application)
      return

    # Shows the details
    self.prepended_details.get_buffer().set_text(self.backend.prepended_data)
    self.appened_details.get_buffer().set_text(self.backend.appened_data)

  # CALLBACKS
  def cb_close_application(self, widget, event, data=None):
    """Callback function for the main window's close event
    
    """
    self.close_application()
    return False

  def cb_close_application(self, widget, data=None):
    """Callback function for the main window's close event
    
    """
    self.close_application()
    return False

  def cb_show_about(self, widget, data=None):
    """Callback function to show the "about" dialog
    
    """
    self.show_about_dialog()
    return False

  def cb_send_message(self, widget, data=None):
    """Callback function to actually send the message
    
    """

    self.main_window.set_sensitive(False)

    self.backend.subject = self.subject.get_text()
    self.backend.message = self.message.get_buffer().get_text(
                           self.message.get_buffer().get_start_iter(),
                           self.message.get_buffer().get_end_iter())
    try:
      self.backend.send()
    except encryption.EncryptionException, e:
      self.show_exception_dialog(_("An error occured during encryption."), e)
      return False
    except encryption.KeyNotFoundException, e:
      self.show_exception_dialog(_("Unable to find encryption key."), e)
      return False
    except smtplib.SMTPException, e:
      self.show_exception_dialog(_("Unable to send the mail."), e)
      return False
    except Exception, e:
      self.show_exception_dialog(_("Unable to create or to send the mail."), e)
      return False

    dialog = gtk.MessageDialog(parent=self.main_window,
                               flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_INFO,
                               buttons=gtk.BUTTONS_CLOSE,
                               message_format=_("Your message has been sent."))
    dialog.connect("response", self.cb_close_application)
    dialog.show()

    return False

  def show_exception_dialog(self, message, exception,
                            close_callback = None):
    """Shows a dialog reporting an exception
    
    @param message A string explaining the exception
    @param exception The exception
    @param close_callback An alternative callback to use on closing
    """

    if not close_callback:
      close_callback = self.cb_close_exception_dialog

    dialog = gtk.MessageDialog(parent=self.main_window,
                               flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_ERROR,
                               buttons=gtk.BUTTONS_CLOSE)
    dialog.set_markup("<b>%s</b>\n\n%s\n" % (message, exception.message))
    
    dialog.connect("response", close_callback)
    dialog.show()
    print traceback.format_exc()

  def cb_close_exception_dialog(self, widget, data=None):
    """Callback function for the exception dialog close event
    
    """
    self.main_window.set_sensitive(True)
    widget.destroy()
    return False

  def show_about_dialog(self):
    """Shows an "about" dialog for the program
    
    """

    # Creates the about dialog
    about_dialog = gtk.AboutDialog()
    about_dialog.set_transient_for(self.main_window)
    about_dialog.set_version(__version__)
    about_dialog.set_name(_("WhisperBack"))
    about_dialog.set_comments(_("Send a feedback in an encrypted mail."))
    about_dialog.set_license(__licence__)
    about_dialog.set_copyright(_("Copyright © 2009 amnesia@boum.org"))
    about_dialog.set_authors(["_(Amnesia team <amnesia@boum.org>)"])
    about_dialog.set_translator_credits(_("translator-credits"))
    about_dialog.set_website("https://amnesia.boum.org")
    about_dialog.connect("response", gtk.Widget.hide_on_delete)
    about_dialog.show()

  def close_application(self):
    """
    Closes the application
    
    """
    gtk.main_quit()

########################################################################

class WhisperBack(object):
  """
  This class contains the backend which actually sends the feedback
  """
  
  def __init__(self, subject = "", message = ""):
    """Initialize a feedback object with the given contents
    
    @param subject The topic of the feedback 
    @param message The content of the feedback
    """
    # Initialize config variables
    self.to_address = None
    self.to_fingerprint = None
    self.from_address = None
    self.mail_prepended_info = lambda: ""
    self.mail_appened_info = lambda: ""
    self.mail_subject = None
    self.smtp_host = None
    self.smtp_port = None
    self.smtp_tlscafile = None

    # Load the python configuration file "config.py" from diffrents locations
    #FIXME this is an absolute path, bad !
    self.__load_conf(os.path.join("/", "etc", "whisperback", "config.py"))
    self.__load_conf(os.path.join(os.path.expanduser('~'),
                                  ".whisperback",
                                  "config.py"))
    self.__load_conf(os.path.join(os.getcwd(), "config.py"))
    self.__check_conf()

    # Get additional info through the callbacks
    self.prepended_data = self.mail_prepended_info()
    print self.prepended_data
    self.appened_data = self.mail_appened_info()

    # Initialize other variables
    self.subject = subject
    self.message = message

  def __load_conf(self, config_file_path):
    """Loads a configuration file from config_file_path and executes it
    inside the current class.
    
    @param config_file_path The path on the configuration file to load
    """

    f = None

    try:
        f = open(config_file_path, 'r')
        code = f.read()
    except IOError:
        # There's no problem if one of the configuration file is not
        # present
        return None
    finally:
        if f:
            f.close()

    exec code in self.__dict__

  def __check_conf(self):
    """Check that all the required configuration variables are filled
    and raise MisconfigurationException if not.
    """

    # XXX: Sanity checks

    if not self.to_address:
        raise MisconfigurationException('to_address')
    if not self.to_fingerprint:
        raise MisconfigurationException('to_fingerprint')
    if not self.from_address:
        raise MisconfigurationException('from_address')
    if not self.mail_subject:
        raise MisconfigurationException('mail_subject')
    if not self.smtp_host:
        raise MisconfigurationException('smtp_host')
    if not self.smtp_port:
        raise MisconfigurationException('smtp_port')
    if not self.smtp_tlscafile:
        raise MisconfigurationException('smtp_tlscafile')

  def send(self):
    """Actually sends the message"""
    
    message_body = "Subject: %s\n%s\n%s\n%s\n" %(self.subject,
                                                 self.prepended_data,
                                                 self.message,
                                                 self.appened_data)
/bin/bash: q : commande introuvable
    encrypted_message_body = encryption.Encryption(). \
                             encrypt(message_body, [self.to_fingerprint])
    
    mail.create_message(self.from_address, self.to_address,
                         self.mail_subject, encrypted_message_body)
    
    mail.send_message_tls(self.from_address, self.to_address,
                            encrypted_message_body, self.smtp_host,
                            self.smtp_port, self.smtp_tlscafile)

########################################################################

class MisconfigurationException(Exception):
  """This exception is raised when the configuartion can't be properly
  loaded

  """
  def __init__(self, variable):
    Exception.__init__(self, _("The variable %s was not found in any of the configuation files /etc/whisperback/config.py, ~/.whisperback/config.py, ./config.py") % variable)

