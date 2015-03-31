#!/usr/bin/env python
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

    # We set a long timeout because Tor is slow
    smtp = smtplib.SMTP(timeout=120, host=host, port=port)
    (resp, reply) = smtp.starttls(context=create_ssl_context(tls_cafile))
    # Default python let you continue in cleartext if starttls
    # fails, while you expect to have an encrypted connexion
    if resp != 220:
        raise TLSError("%s answered %i, %s when trying to start TLS"
                       % (host, resp, reply))
    else:
        smtp.sendmail(from_address, [to_address], message)
        smtp.quit()

def create_ssl_context(tls_cafile):
    """Creates an SSLContext appropriate for use in WhisperBack

    @param tls_cafile Certificate authority file
    @returns An SSLContext
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.load_verify_locations(cafile=tls_cafile)
    context.verify_mode = ssl.CERT_REQUIRED
    # disable compression to prevent CRIME attacks (OpenSSL 1.0+)
    # this is copied from python's SSL module source
    context.options |= ssl.OP_NO_COMPRESSION
    return context

class TLSError(Exception):
    """Exception raised if problem happens in STARTTLS step"""
    pass
