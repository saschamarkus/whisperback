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
# setup.py
#
# Setup file
#
########################################################################

from distutils.core import setup
from DistUtilsExtra.command import *
import os
import subprocess

# Some ugly way to generate the headers required to use gettext whit glade
intltool_extract = subprocess.Popen (["intltool-extract",
                                     "--type=gettext/glade",
                                     "data/whisperback.xml"])
intltool_extract.wait()

# And some ugly way to generate the man
txt2tags = subprocess.Popen (["txt2tags",
                              "--outfile=doc/whisperback.1",
                              "doc/whisperback.t2t"])
txt2tags.wait()

setup(name='whisperback',
    version='0.1',
    description='Send a feedback in an encrypted mail',
    author='Amnesia',
    author_email='amnesia@boum.org',
    packages=['whisperBack'],
    scripts=['whisperback'],
    data_files=[('share/whisperback', ['data/whisperback.xml']),
                ('share/pixmaps', ['data/whisperback.svg']),
                ('share/applications', ['data/whisperback.desktop']),
                ('share/doc/whisperback', ['config.sample', 
                                           'doc/README']),
                ('share/man', ['doc/whisperback.1'])],
    cmdclass = { "build" : build_extra.build_extra,
        "build_i18n" :  build_i18n.build_i18n,
        "build_help" :  build_help.build_help,
        "build_icons" :  build_icons.build_icons,
        "clean": clean_i18n.clean_i18n,
        }
    )
