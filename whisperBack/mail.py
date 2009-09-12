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


# Import smtplib for the actual sending function
import smtplib
import socket
# Import the email modules we'll need
from email.mime.text import MIMEText


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
                  port=25, tls_keyfile=None, tls_certfile=None):
  """Sends a mail
  
  This is from an example from doc.python.org
  
  @param from_address The sender's address
  @param to_address The recipient address
  @param message The content of the mail
  @param host The host of the smtp server to connect to
  @param port The port of the smtp server to connect to
  @param tls_keyfile Keyfile passed to the socket module’s ssl() function.
  @param tls_certfile Certfile passed to the socket module’s ssl() function.
  """
  # We set a long timeout because Tor is slow
  # TODO this will not be necessary anymore under python 2.6, because it
  #      includes a timeout argument on smtplib
  socket.setdefaulttimeout(60)
  
  # Send the message via our own SMTP server, but don't include the
  # envelope header.
  smtp = smtplib.SMTP()
  smtp.connect(host, port)
  smtp.starttls(tls_keyfile, tls_certfile)
  smtp.sendmail(from_address, [to_address], message)
  smtp.quit()
  
