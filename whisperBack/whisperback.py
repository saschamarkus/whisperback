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

########################################################################
#
# whisperback.py
#
# WhisperBack main backend
#
########################################################################

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
import threading

# Import our modules
import exceptions
import mail
import encryption
import utils

class WhisperBack(object):
  """
  This class contains the backend which actually sends the feedback
  """
  
  def set_contact_email(self, email):
    if utils.is_valid_email(email):
       self._contact_email = email
    else:
       #XXX use a better exception
       raise ValueError, _("Invalid contact email: %s" % email)

  contact_email = property(lambda self: self._contact_email,
                           set_contact_email)

  def set_contact_gpgkey(self, gpgkey):
    if (utils.is_valid_pgp_block(gpgkey) or
        utils.is_valid_pgp_id(gpgkey) or
        utils.is_valid_link(gpgkey)):
       self._contact_gpgkey = gpgkey
    else:
       #XXX use a better exception
       if len(gpgkey.splitlines()) <= 1:
           message = _("Invalid contact OpenPGP key: %s" % gpgkey)
       else:
           message = _("Invalid contact OpenPGP public key block")
       raise ValueError, message

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
        raise exceptions.MisconfigurationException('to_address')
    if not self.to_fingerprint:
        raise exceptions.MisconfigurationException('to_fingerprint')
    if not self.from_address:
        raise exceptions.MisconfigurationException('from_address')
    if not self.mail_subject:
        raise exceptions.MisconfigurationException('mail_subject')
    if not self.smtp_host:
        raise exceptions.MisconfigurationException('smtp_host')
    if not self.smtp_port:
        raise exceptions.MisconfigurationException('smtp_port')
    if not self.smtp_tlscafile:
        raise exceptions.MisconfigurationException('smtp_tlscafile')

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
        # Test whether we have a key block or a key id/url
        if len(self.contact_gpgkey.splitlines()) <= 1:
            body += "OpenPGP-Key: %s\n" % self.contact_gpgkey
        else:
            body += "OpenPGP-Key: included below\n"
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
