# Copyright 2020 Pascal COMBES <pascom@orange.fr>
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

from warnings import warn
from selenium.common import exceptions as selenium

class JavascriptPropertyDescriptor:
    def __init__(self, propertyName):
        self.__propertyName = propertyName

    def __get__(self, obj, owner=None):
        return obj.execute_script(f"return {self.__propertyName};")

    def __set__(self, obj, value=None):
        try:
            obj.execute_script(f"{self.__propertyName} = {value};")
        except selenium.JavascriptException as e:
            jsError, sep, msg = e.msg.partition(': ')
            if (jsError == 'TypeError'):
                raise TypeError(msg)
            elif (jsError == 'RangeError'):
                raise ValueError(msg)
            elif (jsError == 'ReferenceError'):
                raise NameError(msg)
            else:
                raise


def captureConsole(browser, xpiPath):
    """
        Install **ConsoleCapture** on the given WebDriver

        Call this function to install **ConsoleCapture** on a WebDriver.
        After having called this function, you will be able to get the capture
        using ``browser.getConsoleCapture()`` and clear it using
        ``browser.clearConsoleCapture()`` and access the capture depth using
        the ``captureDepth`` property.

        *Note*: You should provide a non-``None`` profile when initializing the
        WebDriver, unless you use a signed extension.

        *Parameters*:
            - **browser**: The Selenium WebDriver in which to install **ConsoleCapture**
            - **xpiPath**: The path to **ConsoleCapture** extension file.
    """

    if hasattr(browser, 'getConsoleCapture') and hasattr(browser, 'clearConsoleCapture'):
        warn("ConsoleCapture is alredy installed in this browser.", RuntimeWarning, stacklevel=2)
        return

    if browser.profile is not None:
        browser.profile.set_preference('xpinstall.signatures.required', False)
    else:
        warn("You should give non-None profile when initializing the WebDriver.", RuntimeWarning)
    print(browser.install_addon(xpiPath, False))

    setattr(browser, 'getConsoleCapture', lambda: browser.execute_script('return console.capture.get();'))
    setattr(browser, 'clearConsoleCapture', lambda: browser.execute_script('console.capture.clear();'))
    setattr(type(browser), 'captureDepth', JavascriptPropertyDescriptor('console.capture.depth'))
