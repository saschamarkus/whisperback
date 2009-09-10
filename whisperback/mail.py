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


def send_message (from_address, to_address, message):
  """Sends a mail
  
  This is from an example from doc.python.org
  
  @param from_address The sender's address
  @param to_address The recipient address
  @param message The content of the mail
  """
  # Send the message via our own SMTP server, but don't include the
  # envelope header.
  smtp = smtplib.SMTP()
  smtp.sendmail(from_address, [to_address], message)
  smtp.quit()
