REPOSITORY DESCRIPTION
----------------------

This repository contains a small extension allowing to capture the console
calls in Firefox. This allows Selenium to retrieve them. 
The code is relatively generic and can easily be extended to capture calls
to any object.

You can reuse it freely under the terms of the GPL version 3 (see the 
LICENSE file of this repository, or below for a short note).

FEATURES
--------

Here is the list of the current features (included in version 0.1)
- Capture calls to members with:
  - Arguments
  - Caller name, file, line and column

Ideas I have to extend the functionalities of the page are listed
[below](#future-developments)

FUTURE DEVELOPMENTS
-------------------

Here is the list of ideas I would like to implement
- Make the code even more generic, so that user can choose programmatically
which object to capture.

If you have any other feature you will be interested in, please let me know.
I will be pleased to develop it if I think it is a must have.

If you want to implement extension, also tell me please. Admittedly you
can do what you desire with the code (under the
[licensing constraints](#licensing-information)), but this will avoid double work.


BUILDING
--------

The script [build.sh](https://github.com/pasccom/ConsoleCapture/blob/master/build.sh)
allows to easily build the extension into an `*.xpi` file.

*WARNING:* The extension is unsigned, hence you have to ensure that the preference
`xpinstall.signatures.required` is set to `false`.

LICENSING INFORMATION
---------------------
These programs are free software: you can redistribute them and/or modify
them under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

These programs are distributed in the hope that they will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
