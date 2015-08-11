#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send feedback in an encrypted mail
# Copyright (C) 2009-2015 Tails developers <tails@boum.org>
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

"""WhisperBack mailing library

"""

import smtplib
import ssl
import time
import socket
import socks

#pylint: disable=R0913
def send_message_tls (from_address, to_address, message, host="localhost",
                      port=25, tls_cafile=None):
    """Sends a mail

    Send the message via our own SMTP server, but don't include the
    envelope header. This is based on an example from doc.python.org

    @param from_address The sender's address
    @param to_address The recipient address
    @param message The content of the mail
    @param host The host of the smtp server to connect to
    @param port The port of the smtp server to connect to
    @param tls_cafile Certificate authority file used to create the SSLContext
    """

    # Monkeypatching the entire connection through the SOCKS proxy
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
    socket.socket = socks.socksocket

    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                            cafile=tls_cafile)
    # We set a long timeout because Tor is slow
    smtp = smtplib.SMTP(timeout=120, host=host, port=port)
    (resp, reply) = smtp.starttls(context=ssl_context)
    # Default python let you continue in cleartext if starttls
    # fails, while you expect to have an encrypted connexion
    if resp != 220:
        raise TLSError("%s answered %i, %s when trying to start TLS"
                       % (host, resp, reply))
    else:
        smtp.sendmail(from_address, [to_address], message)
        smtp.quit()

class TLSError(Exception):
    """Exception raised if problem happens in STARTTLS step"""
    pass
