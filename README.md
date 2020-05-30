REPOSITORY DESCRIPTION
----------------------

This repository contains a small extension allowing to capture the console
calls in Firefox. This allows Selenium to retrieve them. 
The code is relatively generic and can easily be extended to capture calls
to any object (see documentation in
[console_capture.js](https://github.com/pasccom/ConsoleCapture/blob/master/console_capture.js).

You can reuse it freely under the terms of the GPL version 3 (see the 
LICENSE file of this repository, or below for a short note).

FEATURES
--------

Here is the list of the current features (included in version 2.0)
- Capture calls to members with:
  - Arguments (basic types, arrays and objects are supported)
  - Caller name, file, line and column
- Special handling of DOM elements so that they are returned as Selenium `WebElements`
- Configure capture depth for complex objects (to avoid recusion loops).
- Python wrapper to be used with Selenium.

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

BUILDING DOCUMENTATION
----------------------

The documentation of the helper included in ConsoleCapture is provided as
Sphinx reStructuredText, which can be compiled into beatiful documentation
by [Sphinx](http://www.sphinx-doc.org).

To compile the documentation you have to install Sphinx in the `virtualenv`,
which can be done using
```
source env/bin/activate
pip install -U sphinx
```
If you are using Unix, you will also need `make`, which is generally provided
by default.

Then `cd` into the `doc` subdirectory and run e.g.
```
make html
```
to generate HTML documentation. The documentation is output in `doc/_build` by default.

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
