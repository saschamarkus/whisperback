#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
__licence__ = """
WhisperBack - Send a feedback in an encrypted mail
Copyright (C) 2009-2010 Amnesia <amnesia@boum.org>

This file is part of WhisperBack

WhisperBack is  free software; you can redistribute  it and/or modify
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

__version__ = '1.3-dev'
LOCALEDIR = "locale/"
PACKAGE = "whisperback"

########################################################################
#
# WhisperBack.py
#
# WhisperBack main backend and GUI
#
########################################################################

import pygtk
pygtk.require('2.0')
import gtk
import gobject
# Workaround an API change: timeout_add was moved from gobject to glib
# in 2.16
if gobject.pygobject_version[:2] >= (2, 16):
    import glib
else:
    class glib:
        timeout_add = gobject.timeout_add
gobject.threads_init()

import os
import types
import threading

# Used to by show_exception_dialog to print exception traceback
import traceback

# Import these because we need the exception they raise
import smtplib
import socket

# Import our modules
import mail
import encryption
import utils

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
                                      "whisperback.ui"))
    builder.connect_signals(self)

    self.main_window = builder.get_object("windowMain")
    self.progression_dialog = builder.get_object("dialogProgression")
    self.progression_main_text = builder.get_object("progressLabelMain")
    self.progression_progressbar = builder.get_object("progressProgressbar")
    self.progression_secondary_text = builder.get_object("progressLabelSecondary")
    self.progression_close = builder.get_object("progressButtonClose")
    self.gpg_dialog = builder.get_object("dialogGpgkeyblock")
    self.gpg_keyblock = builder.get_object("textviewGpgKeyblock")
    self.gpg_ok = builder.get_object("buttonGpgOk")
    self.gpg_cancel = builder.get_object("buttonGpgClose")
    self.subject = builder.get_object("entrySubject")
    self.message = builder.get_object("textviewMessage")
    self.contact_email = builder.get_object("entryMail")
    self.contact_gpg_useid = builder.get_object("radiobuttonGPGKeyId")
    self.contact_gpg_usefile = builder.get_object("radiobuttonGPGKeyfile")
    self.contact_gpg_keyid = builder.get_object("entryGPGKeyId")
    self.contact_gpg_keyblock = builder.get_object("buttonGPGKeyBlock")
    self.prepended_details = builder.get_object("textviewPrependedInfo")
    self.include_prepended_details = builder.get_object("checkbuttonIncludePrependedInfo")
    self.appended_details = builder.get_object("textviewAppendedInfo")
    self.include_appended_details = builder.get_object("checkbuttonIncludeAppendedInfo")
    self.send_button = builder.get_object("buttonSend")

    try:
      self.main_window.set_icon_from_file(os.path.join(
          utils.get_pixmapdir(), "whisperback.svg"))
    except gobject.GError, e:
      print e

    self.main_window.show()

    # Launches the backend
    try:
      self.backend = WhisperBack()
    except MisconfigurationException, e:
      self.show_exception_dialog(_("Unable to load a valid configuration."), e, self.cb_close_application)
      return

    # Shows the debugging details
    self.prepended_details.get_buffer().set_text(self.backend.prepended_data)
    self.appended_details.get_buffer().set_text(self.backend.appended_data)

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

  def cb_enter_gpgkeyblock(self, widget, data=None):
    """Callback function to show the gpg publick key block input dialog

    """
    self.show_gpg_dialog()
    return False

  def cb_contact_gpg_togglesensitive(self, widget, data=None):
    self.contact_gpg_keyblock.set_sensitive(not self.contact_gpg_keyblock.get_sensitive())
    self.contact_gpg_keyid.set_sensitive(not self.contact_gpg_keyid.get_sensitive())

  def cb_send_message(self, widget, data=None):
    """Callback function to actually send the message
    
    """

    self.progression_main_text.set_text(_("Sending mail"))
    self.progression_secondary_text.set_text(_("This could take a while..."))
    self.progression_dialog.set_transient_for(self.main_window)
    self.progression_dialog.show()
    self.main_window.set_sensitive(False)

    self.backend.subject = self.subject.get_text()
    self.backend.message = self.message.get_buffer().get_text(
                           self.message.get_buffer().get_start_iter(),
                           self.message.get_buffer().get_end_iter())
    if self.contact_email.get_text():
        try:
            self.backend.contact_email = self.contact_email.get_text()
        except ValueError, e:
            self.show_exception_dialog(_("The contact email adress doesn't seem valid."), e)
            self.progression_dialog.hide()
            return
    if self.contact_gpg_useid.get_active() and self.contact_gpg_keyid.get_text():
        try:
            self.backend.contact_gpgkey = self.contact_gpg_keyid.get_text()
        except ValueError, e:
            self.show_exception_dialog(_("Invalid contact GPG key ID."), e)
            self.progression_dialog.hide()
            return
    # else, contact_gpgkey was filled when the user exited the dedicated dialog

    if not self.include_prepended_details.get_active():
        self.backend.prepended_data = ""
    if not self.include_appended_details.get_active():
        self.backend.appended_data = ""

    def cb_update_progress():
        self.progression_progressbar.pulse()

    def cb_finished_progress(e):
        if isinstance(e, smtplib.SMTPException):
            self.show_exception_dialog(_("Unable to send the mail : SMTP error"), e)
            self.progression_dialog.hide()
        elif isinstance(e, socket.error):
            self.show_exception_dialog(_("Unable to connect to the server."), e)
            self.progression_dialog.hide()
        elif isinstance(e, Exception):
            self.show_exception_dialog(_("Unable to create or to send the mail."), e)
            self.progression_dialog.hide()
        else:
            self.main_window.set_sensitive(False)
            self.progression_close.set_sensitive(True)
            self.progression_progressbar.set_fraction(1.0)
            self.progression_main_text.set_text(_("Your message has been sent."))
            self.progression_secondary_text.set_text("")

    try:
        self.backend.send(cb_update_progress, cb_finished_progress)
    except encryption.EncryptionException, e:
        self.show_exception_dialog(_("An error occured during encryption."), e)
        self.progression_dialog.hide()
    except encryption.KeyNotFoundException, e:
        self.show_exception_dialog(_("Unable to find encryption key."), e)
        self.progression_dialog.hide()

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

    if isinstance(exception.message, types.MethodType):
        exception_message = exception.message()
    else:
        exception_message = str(exception)

    dialog = gtk.MessageDialog(parent=self.main_window,
                               flags=gtk.DIALOG_MODAL,
                               type=gtk.MESSAGE_ERROR,
                               buttons=gtk.BUTTONS_CLOSE,
                               message_format=message)
    dialog.format_secondary_text(exception_message)
    
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

  def show_gpg_dialog(self):
    """Show a text entry dialog to let the user enter a GPG public key block

    """
    if self.backend.contact_gpgkey:
        self.gpg_keyblock.get_buffer().set_text(str(self.backend.contact_gpgkey))
    else:
        self.gpg_keyblock.get_buffer().set_text("")
    self.gpg_dialog.show()

  def cb_gpg_close_ok(self, widget, data=None):
    """Callback function for the gpg publick key entry close and apply event

    """
    try:
        self.backend.contact_gpgkey = self.gpg_keyblock.get_buffer().get_text(
            self.gpg_keyblock.get_buffer().get_start_iter(),
            self.gpg_keyblock.get_buffer().get_end_iter())
    except ValueError, e:
        self.show_exception_dialog(_("Invalid GPG public key block."), e)
        return
    self.gpg_dialog.hide()

  def cb_gpg_close_cancel(self, widget, data=None):
    """Callback function for the gpg pyblick key entry cancel event

    """
    self.gpg_dialog.hide()

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
  
  def set_contact_email(self, email):
    if utils.check_email(email):
       self._contact_email = email
    else:
       #XXX use a better exception
       raise ValueError, _("Invalid contact email: %s" % email)

  contact_email = property(lambda self: self._contact_email,
                           set_contact_email)

  def set_contact_gpgkey(self, gpgkey):
    if utils.check_gpgkey(gpgkey):
       self._contact_gpgkey = gpgkey
    else:
       #XXX use a better exception
       raise ValueError, _("Invalid contact gpg key: %s" % gpgkey)

  contact_gpgkey = property(lambda self: self._contact_gpgkey,
                           set_contact_gpgkey)

  def __init__(self, subject = "", message = ""):
    """Initialize a feedback object with the given contents
    
    @param subject The topic of the feedback 
    @param message The content of the feedback
    """
    self.__thread = None

    # Initialize config variables
    self.to_address = None
    self.to_fingerprint = None
    self.from_address = None
    self.mail_prepended_info = lambda: ""
    self.mail_appended_info = lambda: ""
    self.mail_subject = None
    self.smtp_host = None
    self.smtp_port = None
    self.smtp_tlscafile = None

    # Load the python configuration file "config.py" from diffrents locations
    # XXX: this is an absolute path, bad !
    self.__load_conf(os.path.join("/", "etc", "whisperback", "config.py"))
    self.__load_conf(os.path.join(os.path.expanduser('~'),
                                  ".whisperback",
                                  "config.py"))
    self.__load_conf(os.path.join(os.getcwd(), "config.py"))
    self.__check_conf()

    # Get additional info through the callbacks
    self.prepended_data = self.mail_prepended_info()
    print self.prepended_data
    self.appended_data = self.mail_appended_info()

    # Initialize other variables
    self.subject = subject
    self.message = message
    self._contact_email = None
    self._contact_gpgkey = None

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
        # There's no problem if one of the configuration files is not
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

    # XXX: Add sanity checks
    
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

  def execute_threaded(self, func, args, progress_callback=None, 
                       finished_callback=None, polling_freq=100):
    """Execute a function in another thread and handle it.
    
    Execute the function `func` with arguments `args` in another thread,
    and poll whether the thread is alive, executing the callback
    `progress_callback` every `polling_frequency`. When the function
    thread terminates, saves the execption it eventually raised and pass
    it to `finished_callback`.
    
    @param func               the function to execute.
    @param args               the tuple to pass as arguments to `func`.
    @param progress_callback  (optional) a callback function to call
                              every time the execution thread is polled.
                              It doesn't take any agument. 
    @param finished_callback  (optional) a callback function to call when
                              the execution thread terminated. It receives
                              the exception raised by `func`, if any, or
                              None.
    @param polling_freq       (optional) the interal between polling
                              iterations (in ms).
    """
    def save_exception(func, args):
        try:
            func(*args)
        except Exception, e:
            self.__error_output = e
            raise

    def poll_thread(self):
        if progress_callback is not None:
            progress_callback()
        if self.__thread.isAlive():
            return True
        else:
            if finished_callback is not None:
                finished_callback(self.__error_output)
            return False

    self.__error_output = None
    assert self.__thread is None or not self.__thread.isAlive ()
    self.__thread = threading.Thread(target=save_exception, args=(func, args))
    self.__thread.start()
    # XXX: there could be no main loop
    glib.timeout_add(polling_freq, poll_thread, self)
  # XXX: static would be best, but I get a problem with self.*
  #execute_threaded = staticmethod(execute_threaded)

  def __prepare_body(self):
    """Returns the content of the message body

    Aggregate all informations to prepare the message body.
    """
    body = "Subject: %s\n" % self.subject
    if self.contact_email:
        body += "From: %s\n" % self.contact_email
    if self.contact_gpgkey:
        # Test wether we have a key ID or a key block
        if len(self.contact_gpgkey.splitlines()) <= 1:
            body += "GPG-Key: %s\n" % self.contact_gpgkey
        else:
            body += "GPG-Key: included below\n"
    body += "%s\n%s\n\n" % (self.prepended_data, self.message)
    if self.contact_gpgkey and len(self.contact_gpgkey.splitlines()) > 1:
        body += "%s\n\n" % self.contact_gpgkey
    body += "%s\n" % self.appended_data
    return body

  def send(self, progress_callback=None, finished_callback=None):
    """Actually sends the message
    
    @param progress_callback 
    @param finished_callback
    """
    
    # XXX: It's really strange that some exceptions from this method are
    #      raised and some other transmitted to finished_callback…

    message_body = self.__prepare_body()

    encrypted_message_body = encryption.Encryption(). \
                             encrypt(message_body, [self.to_fingerprint])
    
    mime_message = mail.create_message(self.from_address, self.to_address,
                                       self.mail_subject, encrypted_message_body)

    self.execute_threaded(func=mail.send_message_tls,
                          args=(self.from_address, self.to_address,
                                mime_message, self.smtp_host,
                                self.smtp_port, self.smtp_tlscafile),
                          progress_callback=progress_callback,
                          finished_callback=finished_callback)


########################################################################

class MisconfigurationException(Exception):
  """This exception is raised when the configuartion can't be properly
  loaded

  """
  def __init__(self, variable):
    Exception.__init__(self, _("The variable %s was not found in any of the configuation files /etc/whisperback/config.py, ~/.whisperback/config.py, ./config.py") % variable)

