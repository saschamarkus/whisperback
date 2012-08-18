#!/usr/bin/env python
# -*- coding: UTF-8 -*-

########################################################################
# WhisperBack - Send feedback in an encrypted mail
# Copyright (C) 2009-2012 Tails developers <amnesia.org>
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

from distutils.core import setup, Command
from DistUtilsExtra.command import *
import os
import subprocess

class build_gtkbuilderi18n(Command):
    description = "generate the headers required to use gettext whit gtkbuilder"
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        subprocess.call (["intltool-extract",
                          "--type=gettext/glade",
                          "data/whisperback.ui"])

class build_man(Command):
    description = "generate the man"
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        subprocess.call (["txt2tags",
                         "--outfile=doc/whisperback.1",
                         "doc/whisperback.t2t"])

build_extra.build_extra.sub_commands.insert(0, ("build_gtkbuilderi18n", None))
build_extra.build_extra.sub_commands.append(("build_man", None))

setup(name='whisperback',
    version='1.6~rc1',
    description='Send feedback in an encrypted mail',
    author='Tails developers',
    author_email='tails@boum.org',
    license='GNU GPL v3',
    packages=['whisperBack'],
    scripts=['whisperback'],
    data_files=[('share/whisperback', ['data/whisperback.ui', 'data/style.css']),
                ('share/pixmaps', ['data/whisperback.svg']),
                ('share/applications', ['data/whisperback.desktop']),
                ('share/doc/whisperback', ['doc/config.py.sample', 
                                           'README']),
                ('share/man/man1', ['doc/whisperback.1'])],
    requires=['gtk', 'pyme', 'gnutls'],
    cmdclass = { "build" : build_extra.build_extra,
        "build_gtkbuilderi18n" : build_gtkbuilderi18n,
        "build_man" : build_man,
        "build_i18n" :  build_i18n.build_i18n,
        "build_help" :  build_help.build_help,
        "build_icons" :  build_icons.build_icons,
        "clean": clean_i18n.clean_i18n,
        }
    )
