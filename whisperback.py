#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send a feedback in an encrypted mail
# Copyright (C) 2009 Amnesia <amnesia@boum.org>
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
# whisperback
#
# WhisperBack launcher script
#
########################################################################

#import os
import sys
#import optparse
import gtk

import gettext

import whisperback

#program = sys.argv[0]
#if program.startswith('./') or program.startswith('bin/'):
#  sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#    os.environ['USBCREATOR_LOCAL'] = '1'

gettext.install('whisperback', localedir='/usr/share/locale', unicode=True)

# parser = optparse.OptionParser(usage=_('%prog [options]'), version='0.2.5')
# parser.add_option('-s', '--safe', dest='safe', action='store_true',
#                   help=_('choose safer options when constructing the USB '
#                          'disk (may slow down the boot process).'))
# (options, args) = parser.parse_args()

print whisperback
#print whisperback.__all__
ui = whisperback.WhisperBackUI()
gtk.main()
