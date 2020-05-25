/* Copyright 2018-2020 Pascal COMBES <pascom@orange.fr>
 * 
 * This file is part of ConsoleCapture.
 * 
 * ConsoleCapture is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * ConsoleCapture is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with ConsoleCapture. If not, see <http://www.gnu.org/licenses/>
 */

/*!
 * \brief Capture calls to an object
 *
 * Capture every call to an object members.
 * The object must be a children of window object
 * and all its members MUST be functions.
 * The original functions are still available using `.original`
 * \param objName The name of the object to capture.
 */
function capture(objName)
{
    function isA(value, typeName)
    {
        return Object.prototype.toString.call(value) == '[object ' + typeName + ']'
    }

    function clean(value)
    {
        if (isA(value, 'Arguments')) {
            return Array.prototype.map.call(value, clean);
        } else if (isA(value, 'Array')) {
            return value.map(clean);
        } else if (isA(value, 'Boolean') || isA(value, 'Number') || isA(value, 'String')) {
            return value;
        } else if (isA(value, 'Function')) {
            return 'function()';
        } else if (isA(value, 'Object')) {
            var cleanValue = {};
            Object.keys(value).forEach((key) => {
                cleanValue[key] = clean(value[key]);
            });
            return cleanValue;
        } else if (isA(value, 'Error')) {
            return {
                type: 'Error',
                lineNumber: value.lineNumber,
                columnNumber: value.columnNumber,
                fileName: value.fileName,
            };
        } else {
            return Object.prototype.toString.call(value);
        }
    }

    var captured = [];

    var obj = window[objName];
    var newObj = {
        capture: {
            get: () => {
                return cloneInto(captured, window);
            },
            clear: () => {
                captured = [];
            },
        },
        original: {},
    };

    Object.keys(obj).forEach((key) => {
        newObj[key] = function() {
            obj[key](... arguments);

            var cap = {
                callee: key,
                time: Date.now(),
                arguments: clean(arguments),
            };

            var stack = (new Error()).stack.split('\n');
            var stackLineFields = (/^([^@]*)@(.*):(\d+):(\d+)$/).exec(stack[1]);

            if (stackLineFields !== null) {
                cap.caller = stackLineFields[1];
                cap.fileName = stackLineFields[2];
                cap.lineNumber = stackLineFields[3];
                cap.columnNumber = stackLineFields[4];
            }

            captured.push(cap);
        };
        newObj.original[key] = function() {
            obj[key](... arguments);
        };
    });

    window.wrappedJSObject[objName] = cloneInto(newObj, window, {cloneFunctions: true});
}

capture('console');
