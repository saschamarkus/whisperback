#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""WhisperBack GUI

"""

########################################################################
__licence__ = """
WhisperBack - Send feedback in an encrypted mail
Copyright (C) 2009-2012 Tails developers <tails@boum.org>

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

__version__ = '1.6~rc1'
LOCALEDIR = "locale/"
PACKAGE = "whisperback"

import os

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import webkit
import webbrowser

# Used by show_exception_dialog
import traceback
import types

# Import these because we need the exception they raise
import smtplib
import socket

# Import our modules
import whisperBack.exceptions
import whisperBack.whisperback
import whisperBack.utils

#pylint: disable=R0902
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
        builder.set_translation_domain('whisperback')
        builder.add_from_file(os.path.join(whisperBack.utils.get_datadir(),
                                          "whisperback.ui"))
        builder.connect_signals(self)

        self.main_window = builder.get_object("windowMain")
        self.vbox_top_left = builder.get_object("vboxTopLeft")
        self.progression_dialog = builder.get_object("dialogProgression")
        self.progression_main_text = builder.get_object("progressLabelMain")
        self.progression_progressbar = builder.get_object("progressProgressbar")
        self.progression_secondary_text = \
            builder.get_object("progressLabelSecondary")
        self.progression_close = builder.get_object("progressButtonClose")
        self.gpg_dialog = builder.get_object("dialogGpgkeyblock")
        self.gpg_keyblock = builder.get_object("textviewGpgKeyblock")
        self.gpg_ok = builder.get_object("buttonGpgOk")
        self.gpg_cancel = builder.get_object("buttonGpgClose")
        self.subject = builder.get_object("entrySubject")
        self.message = builder.get_object("textviewMessage")
        self.contact_email = builder.get_object("entryMail")
        self.contact_gpg_keyblock = builder.get_object("buttonGPGKeyBlock")
        self.prepended_details = \
            builder.get_object("textviewPrependedInfo")
        self.include_prepended_details = \
            builder.get_object("checkbuttonIncludePrependedInfo")
        self.appended_details = builder.get_object("textviewAppendedInfo")
        self.include_appended_details = \
            builder.get_object("checkbuttonIncludeAppendedInfo")
        self.help_container = builder.get_object("scrolledwindowHelp")
        self.send_button = builder.get_object("buttonSend")

        try:
            self.main_window.set_icon_from_file(os.path.join(
                whisperBack.utils.get_pixmapdir(), "whisperback.svg"))
        except gobject.GError, e:
            print e

        underline = lambda str: str + "\n" + len(str) * '-'

        #pylint: disable=C0301
        self.message.get_buffer().insert_with_tags(
            self.message.get_buffer().get_start_iter(),
                underline ( _("Name of the affected software") ) + "\n"*4 +
                underline ( _("Exact steps to reproduce the problem") ) + "\n"*4 +
                underline ( _("Actual result / the problem") ) + "\n"*4 +
                underline ( _("Desired result") ) + "\n"*4,
            self.message.get_buffer().create_tag(family="Monospace"))

        #pylint: disable=E1101
        self.htmlhelp = webkit.WebView()

        # Load only local ressources in the embedded webkit
        # Loading untrusted ressources in such an unprotected browser
        # wouldn't be safe
        #pylint: disable=C0111,R0913
        def cb_request_starting(web_view, web_frame, web_ressource, request,
                                response, user_data=None):
            if not request.get_uri().startswith("file://"):
                webbrowser.open_new(request.get_uri())
                request.set_uri(web_frame.get_uri())
        self.htmlhelp.connect("resource-request-starting", cb_request_starting)
        self.htmlhelp.get_settings().set_property("user-stylesheet-uri", "file://" +
            whisperBack.utils.get_datadir() + "/style.css")

        # set the two main window areas to be each half of the window
        # on big screens
        if self.main_window.get_screen().get_width() > 800:
            self.vbox_top_left.set_size_request(400, -1)
            self.help_container.set_size_request(400, -1)

        self.main_window.maximize()

        self.main_window.show()

        # Launches the backend
        try:
            self.backend = whisperBack.whisperback.WhisperBack()
        except whisperBack.exceptions.MisconfigurationException, e:
            self.show_exception_dialog(
                _("Unable to load a valid configuration."), e,
                self.cb_close_application)
            return

        # Loads help
        self.load_htmlhelp()
        self.help_container.add_child(builder, self.htmlhelp, None)
        self.htmlhelp.show()

        # Shows the debugging details
        self.prepended_details.get_buffer().set_text(
            self.backend.prepended_data.rstrip())
        self.appended_details.get_buffer().set_text(
            self.backend.appended_data.rstrip())

    # CALLBACKS
    def cb_close_application(self, widget, data=None):
        """Callback function for the main window's close event

        """
        self.close_application()
        return False

    def load_htmlhelp(self):
        """Loads help into the help browser

        """
        self.htmlhelp.load_string(self.backend.html_help,
            "text/html",
            "UTF-8",
            "file:///")

    def cb_help_prev(self, widget, data=None):
        """Callback function to go back in help browser

        """
        if self.htmlhelp.can_go_back():
            self.htmlhelp.go_back()
        else:
            self.load_htmlhelp()

    def cb_show_help(self, widget, data=None):
        """Callback function display help main page in help browser

        """
        self.load_htmlhelp()

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

    def cb_send_message(self, widget, data=None):
        """Callback function to actually send the message

        """

        self.progression_dialog.set_title(_("Sending mail..."))
        self.progression_main_text.set_text(_("Sending mail"))
        #pylint: disable=C0301
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
                self.show_exception_dialog(
                    _("The contact email adress doesn't seem valid."), e)
                self.progression_dialog.hide()
                return

        if not self.include_prepended_details.get_active():
            self.backend.prepended_data = ""
        if not self.include_appended_details.get_active():
            self.backend.appended_data = ""

        #pylint: disable=C0111
        def cb_update_progress():
            self.progression_progressbar.pulse()

        #pylint: disable=C0111
        def cb_finished_progress(e):
            if isinstance(e, Exception):
                if isinstance(e, smtplib.SMTPException):
                    exception_string = _("Unable to send the mail: SMTP error.")
                elif isinstance(e, socket.error):
                    exception_string = _("Unable to connect to the server.")
                else:
                    exception_string = _("Unable to create or to send the mail.")

                if self.backend.send_attempts <= 1:
                    self.show_exception_dialog(exception_string + _("\n\n\
The bug report could not be sent, likely due to network problems. \
Please try to reconnect to the network and click send again.\n\
\n\
If it does not work, you will be offered to save the bug report."), e)
                else:
                    self.show_exception_dialog_with_save(exception_string, e)
                self.progression_dialog.hide()
            else:
                self.main_window.set_sensitive(False)
                self.progression_close.set_sensitive(True)
                self.progression_progressbar.set_fraction(1.0)
                self.progression_main_text.set_text(
                    _("Your message has been sent."))
                self.progression_secondary_text.set_text("")

        try:
            self.backend.send(cb_update_progress, cb_finished_progress)
        except whisperBack.exceptions.EncryptionException, e:
            self.show_exception_dialog(
                _("An error occured during encryption."), e)
            self.progression_dialog.hide()

        return False

    def show_exception_dialog_with_save(self, message, exception):
        """Shows a dialog reporting an exception and prompting the user to
        save the debugging data as a file

        @param message          A string explaining the exception
        @param exception        The exception
        @param close_callback   An alternative callback to use on closing
        @param buttons          Buttons to display
        """
        #pylint: disable=C0111
        def cb_save_response(widget, event, data=None):
            if event == gtk.RESPONSE_ACCEPT:
                try:
                    self.backend.save(widget.get_filename())
                except IOError, e:
                    self.show_exception_dialog(_("Unable to save %s.")
                                               % widget.get_filename(), e)
            widget.hide()
            self.main_window.set_sensitive(True)

        #pylint: disable=C0111
        def cb_response(widget, event, data=None):
            widget.hide()
            if event == gtk.RESPONSE_YES:
                save_dialog = gtk.FileChooserDialog(title=None,
                              parent=self.main_window,
                              action=gtk.FILE_CHOOSER_ACTION_SAVE,
                              buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                       gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))


                save_dialog.set_local_only(True)
                save_dialog.connect("response", cb_save_response)
                save_dialog.show()

            else:
                self.main_window.set_sensitive(True)

        #XXX: fix string
        suggestion = _("The bug report could not be sent, likely \
due to network problems.\n\
\n\
As a work-around you can save the bug report as a file on a USB drive and try \
to send it to us at %s from your email account using another system. \
Note that your bug report will not be \
anonymous when doing so unless you take further steps yourself (e.g. using \
Tor with a throw-away email account).\n\
\n\
Do you want to save the bug report to a file?" % self.backend.to_address)
        self.show_exception_dialog(message + "\n\n" + suggestion, exception,
                                   parent=self.progression_dialog,
                                   close_callback=cb_response,
                                   buttons=gtk.BUTTONS_YES_NO)

    def show_exception_dialog(self, message, exception,
                            close_callback=None, parent=None,
                            buttons=gtk.BUTTONS_CLOSE):
        """Shows a dialog reporting an exception

        @param message          A string explaining the exception
        @param exception        The exception
        @param close_callback   An alternative callback to use on closing
        @param buttons          Buttons to display
        """

        if not close_callback:
            close_callback = self.cb_close_exception_dialog

        if not parent:
            parent = self.main_window

        if isinstance(exception.message, types.MethodType):
            exception_message = exception.message()
        else:
            exception_message = str(exception)

        dialog = gtk.MessageDialog(parent=parent,
                                   flags=gtk.DIALOG_MODAL,
                                   type=gtk.MESSAGE_ERROR,
                                   buttons=buttons,
                                   message_format=message)
        dialog.format_secondary_text(exception_message)
        
        dialog.connect("response", close_callback)
        dialog.show()
        print traceback.format_exc()

    def cb_close_exception_dialog(self, widget, data=None):
        """Callback function for the exception dialog close event
        
        """
        self.main_window.set_sensitive(True)
        widget.hide()
        return False

    def show_about_dialog(self):
        """Shows an "about" dialog for the program
        
        """

        about_dialog = gtk.AboutDialog()
        about_dialog.set_transient_for(self.main_window)
        about_dialog.set_version(__version__)
        about_dialog.set_name(_("WhisperBack"))
        about_dialog.set_comments(_("Send feedback in an encrypted mail."))
        about_dialog.set_license(__licence__)
        about_dialog.set_copyright(
            _("Copyright © 2009-2012 Tails developpers (tails@boum.org)"))
        about_dialog.set_authors([_("Tails developers <tails@boum.org>")])
        about_dialog.set_translator_credits(_("translator-credits"))
        about_dialog.set_website("https://tails.boum.org/")
        about_dialog.connect("response", gtk.Widget.hide_on_delete)
        about_dialog.show()

    def show_gpg_dialog(self):
        """Show a text entry dialog to let the user enter a GPG public key block

        """
        if self.backend.contact_gpgkey:
            #pylint: disable=C0301
            self.gpg_keyblock.get_buffer().set_text(str(self.backend.contact_gpgkey))
        else:
            self.gpg_keyblock.get_buffer().set_text("")
        self.gpg_dialog.show()

    def cb_gpg_close_ok(self, widget, data=None):
        """Callback function for the gpg publick key entry close and apply event

        """
        try:
            #pylint: disable=C0301
            self.backend.contact_gpgkey = self.gpg_keyblock.get_buffer().get_text(
                self.gpg_keyblock.get_buffer().get_start_iter(),
                self.gpg_keyblock.get_buffer().get_end_iter())
        except ValueError, e:
            self.show_exception_dialog(
                _("This doesn's seem to be a valid URL or OpenPGP key."),
                e, parent=self.gpg_dialog)
            return
        self.gpg_dialog.hide()

    def cb_gpg_close_cancel(self, widget, data=None):
        """Callback function for the gpg pyblick key entry cancel event

        """
        self.gpg_dialog.hide()

    #pylint: disable=R0201
    def close_application(self):
        """
        Closes the application

        """
        gtk.main_quit()
