#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send feedback in an encrypted mail
# Copyright (C) 2009-2018 Tails developers <tails@boum.org>
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

import logging
import smtplib
import socket
import socks
import ssl
import time

LOG = logging.getLogger(__name__)

#pylint: disable=R0913
def send_message_tls (from_address, to_address, message, host="localhost",
                      port=25, tls_cafile=None, socks_host="127.0.0.1",
                      socks_port=9050):
    """Sends a mail

    Send the message via our own SMTP server, but don't include the
    envelope header. This is based on an example from doc.python.org

    @param from_address The sender's address
    @param to_address The recipient address
    @param message The content of the mail
    @param host The host of the smtp server to connect to
    @param port The port of the smtp server to connect to
    @param tls_cafile Certificate authority file used to create the SSLContext
    @param socks_host The host of the SOCKS proxy to connect through
    @param socks_port The port of the SOCKS proxy to connect through
    """

    LOG.debug("sending mail")
    # Monkeypatching the entire connection through the SOCKS proxy
    socks.set_default_proxy(socks.SOCKS5, socks_host, socks_port)
    socket.socket = socks.socksocket

    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH,
                                            cafile=tls_cafile)
    try:
        # We set a long timeout because Tor is slow
        smtp = smtplib.SMTP(timeout=120, host=host, port=port)
    except ValueError:
        # socks assumes the host resolves to AF_INET and triggers a ValueError
        # if it's not the case. If a .onion address is given, it resolves to an
        # AF_INET address and to an AF_INET6 address. If the 1st doesn't connect,
        # the 2nd is tried, which make socks trigger the ValueError.
        # This issue is fixed upstream in socks, in which this situation raises
        # a socket.error (https://github.com/Anorov/PySocks/commit/4081b79)
        # XXX: this workaround should be removed when a version of socks containing
        # this commit reaches Tails.
        raise socket.error("PySocks doesn't support IPv6")
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
