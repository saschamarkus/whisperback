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

import pygtk
pygtk.require('2.0')
import gtk
import gettext

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
  """
  
  def __init__ (self, subject, message, details):
    """Sends a feedback with the given contents
    
    @param subject The topic of the feedback 
    @param message The content of the feedback
    @param details The details of the used software
    """
    
    print ("should send a message")
    print ("subject: " + subject)
    print ("message: " + message)
    print ("details: " + details)


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
