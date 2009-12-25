#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send a feedback in an encrypted mail
# Copyright (C) 2009 Amnesio <amnesia@boum.org>
# 
# This program is  free software; you can redistribute  it and/or modify
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
# mail.py
#
# Some tools for mailing
#
########################################################################

import smtplib
import socket
from email.mime.text import MIMEText
import gnutls.errors
import time

def create_message (from_address, to_address, subject, message):
  """Create a plaintext mail
  
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

def send_message_tls (from_address, to_address, message, host="localhost",
                  port=25, tls_cafile=None):
  """Sends a mail
  
  This is from an example from doc.python.org
  
  @param from_address The sender's address
  @param to_address The recipient address
  @param message The content of the mail
  @param host The host of the smtp server to connect to
  @param port The port of the smtp server to connect to
  @param tls_ca Certificate authority file passed to the socket module’s ssl() function.
  """
  # We set a long timeout because Tor is slow
  # XXX: this will not be necessary anymore under python 2.6, because it
  #      includes a timeout argument on smtplib
  socket.setdefaulttimeout(60)
  
  # Send the message via our own SMTP server, but don't include the
  # envelope header.
  smtp = smtplib.SMTP()
  smtp.connect(host, port)
  smtp.starttls(cafile = tls_cafile)
  smtp.sendmail(from_address, [to_address], message)
  smtp.quit()

# This is a monkey patch to make the starttls function of libsmtp use
# starttls, as the buildin doesn't really check certificates and doesn't
# have a timeout parameter
def starttls(self, keyfile = None, certfile = None, cafile=None):
  """Puts the connection to the SMTP server into TLS mode.

  If the server supports TLS, this will encrypt the rest of the SMTP
  session.
  
  """
  (resp, reply) = self.docmd("STARTTLS")
  if resp == 220:
    
      from gnutls.crypto import X509Certificate, X509CRL
      from gnutls.connection import ClientSession, X509Credentials
      import socket, struct
      
      tv = struct.pack('ii', int(6), int(0))
      self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, tv)
      
      if cafile:
        ca = X509Certificate(open(cafile).read())
      # XXX: use CRL
      #crl = X509CRL(open(certs_path + '/crl.pem').read())
      cred = X509Credentials()
      session = ClientSession(self.sock, cred)
      
      while True:
        try:
          session.handshake()
          session.verify_peer()
          break
        except gnutls.errors.OperationWouldBlock:
          time.sleep(0.1)
      
      def tls_quit():
        """Terminate the SMTP session."""
        self.docmd("quit")
        self.sock.bye()
        self.close()
      
      self.quit = tls_quit
      
      self.sock = session
      self.file = SSLFakeFile(session)
      
      # RFC 3207:
      # The client MUST discard any knowledge obtained from
      # the server, such as the list of SMTP service extensions,
      # which was not obtained from the TLS negotiation itself.
      self.helo_resp = None
      self.ehlo_resp = None
      self.esmtp_features = {}
      self.does_esmtp = 0
  return (resp, reply)

class SSLFakeFile:
    """A fake file like object that really wraps a SSLObject.

    It only supports what is needed in smtplib.
    """
    def __init__(self, sslobj):
        self.sslobj = sslobj

    def readline(self):
        str = ""
        chr = None
        while chr != "\n":
          while True:
            try:          
              chr = self.sslobj.recv(1)
              str += chr
              break
            except gnutls.errors.OperationWouldBlock:
              time.sleep(0.1)
        return str

    def close(self):
        pass

smtplib.SMTP.starttls = starttls
