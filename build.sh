#!/bin/sh
# Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
# 
# This file is part of ConsoleCapture.
# 
# ConsoleCapture is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ConsoleCapture is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ConsoleCapture. If not, see <http://www.gnu.org/licenses/>

test -d dist || mkdir dist
zip -r -FS dist/console_capture.xpi manifest.json capture_console.js
